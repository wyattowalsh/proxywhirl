"""Source curation CLI tool for ProxyWhirl.

This script provides tools for validating existing proxy sources and checking
new candidate sources before adding them to the source list.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

import httpx
import typer
from loguru import logger

from proxywhirl import sources
from proxywhirl.models import ProxySourceConfig

app = typer.Typer(help="ProxyWhirl source curation tools")


def _get_variable_name_map() -> dict[str, str]:
    """Build a mapping from source URL to variable name.

    Returns:
        Dictionary mapping source URLs to their variable names in sources.py
    """
    url_to_name = {}
    for name, obj in inspect.getmembers(sources):
        if isinstance(obj, ProxySourceConfig):
            url_to_name[str(obj.url)] = name
    return url_to_name


def _get_source_collections() -> dict[str, list[str]]:
    """Build a mapping of collection names to source URLs.

    Returns:
        Dictionary mapping collection names to lists of source URLs
    """
    collections = {
        "ALL_HTTP_SOURCES": sources.ALL_HTTP_SOURCES,
        "ALL_SOCKS4_SOURCES": sources.ALL_SOCKS4_SOURCES,
        "ALL_SOCKS5_SOURCES": sources.ALL_SOCKS5_SOURCES,
        "RECOMMENDED_SOURCES": sources.RECOMMENDED_SOURCES,
        "API_SOURCES": sources.API_SOURCES,
    }

    url_to_collections = {}
    for collection_name, source_list in collections.items():
        for source in source_list:
            url = str(source.url)
            if url not in url_to_collections:
                url_to_collections[url] = []
            url_to_collections[url].append(collection_name)

    return url_to_collections


def _extract_github_repo(url: str) -> tuple[str, str] | None:
    """Extract owner and repo from a GitHub raw URL.

    Args:
        url: GitHub raw URL

    Returns:
        Tuple of (owner, repo) or None if not a GitHub URL
    """
    if "raw.githubusercontent.com" not in url:
        return None

    parts = url.split("/")
    if len(parts) < 5:
        return None

    owner = parts[3]
    repo = parts[4]
    return owner, repo


def _get_github_metadata(owner: str, repo: str) -> dict[str, Any] | None:
    """Fetch GitHub repository metadata using gh CLI.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Dictionary with stars, last_push, and archived fields, or None if error
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            logger.debug(f"gh CLI failed for {owner}/{repo}: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        return {
            "stars": data.get("stargazers_count", 0),
            "last_push": data.get("pushed_at", "unknown"),
            "archived": data.get("archived", False),
        }
    except FileNotFoundError:
        logger.debug("gh CLI not found, skipping GitHub metadata enrichment")
        return None
    except subprocess.TimeoutExpired:
        logger.debug(f"gh CLI timeout for {owner}/{repo}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Failed to parse gh CLI output for {owner}/{repo}: {e}")
        return None


@app.command()
def validate(
    output_json: bool = typer.Option(True, "--json/--no-json", help="Output results as JSON"),
    timeout: float = typer.Option(15.0, "--timeout", help="Request timeout in seconds"),
    concurrency: int = typer.Option(20, "--concurrency", help="Maximum concurrent requests"),
) -> None:
    """Validate all proxy sources and output detailed report.

    This command validates all sources in ALL_SOURCES, enriches them with
    GitHub metadata, and outputs a structured JSON report.
    """
    logger.info(f"Validating {len(sources.ALL_SOURCES)} proxy sources...")

    report = asyncio.run(
        sources.validate_sources(
            sources=sources.ALL_SOURCES, timeout=timeout, concurrency=concurrency
        )
    )

    logger.info(f"Validation complete: {report.healthy_sources}/{report.total_sources} healthy")

    url_to_name = _get_variable_name_map()
    url_to_collections = _get_source_collections()

    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": report.total_sources,
        "healthy": report.healthy_sources,
        "unhealthy": report.unhealthy_sources,
        "sources": [],
    }

    for result in report.results:
        url = str(result.source.url)
        variable_name = url_to_name.get(url, "UNKNOWN")
        collections_list = url_to_collections.get(url, [])

        source_data = {
            "name": result.name,
            "variable_name": variable_name,
            "url": url,
            "status": "healthy" if result.is_healthy else "unhealthy",
            "status_code": result.status_code,
            "content_length": result.content_length,
            "response_time_ms": round(result.response_time_ms, 2),
            "has_proxies": result.has_proxies,
            "error": result.error,
            "github_stars": None,
            "github_last_push": None,
            "github_archived": None,
            "trusted": result.source.trusted,
            "protocol": result.source.protocol,
            "collections": collections_list,
        }

        github_info = _extract_github_repo(url)
        if github_info:
            owner, repo = github_info
            metadata = _get_github_metadata(owner, repo)
            if metadata:
                source_data["github_stars"] = metadata["stars"]
                source_data["github_last_push"] = metadata["last_push"]
                source_data["github_archived"] = metadata["archived"]

        output_data["sources"].append(source_data)

    if output_json:
        print(json.dumps(output_data, indent=2))
    else:
        typer.echo("\nValidation Summary:")
        typer.echo(f"  Total sources: {output_data['total']}")
        typer.echo(f"  Healthy: {output_data['healthy']}")
        typer.echo(f"  Unhealthy: {output_data['unhealthy']}")
        typer.echo("\nTop issues:")
        for source in output_data["sources"]:
            if source["status"] == "unhealthy":
                typer.echo(f"  - {source['name']}: {source['error'] or 'No proxies found'}")


@app.command()
def check_candidate(
    url: str = typer.Argument(..., help="URL to check as potential proxy source"),
    timeout: float = typer.Option(10.0, "--timeout", help="Request timeout in seconds"),
) -> None:
    """Check if a URL is a valid proxy source candidate.

    This command fetches the URL, analyzes its content, and reports whether
    it appears to be a valid proxy source.
    """
    result = asyncio.run(_check_candidate_async(url, timeout))
    print(json.dumps(result, indent=2))


async def _check_candidate_async(url: str, timeout: float) -> dict[str, Any]:
    """Async implementation of candidate checking.

    Args:
        url: URL to check
        timeout: Request timeout in seconds

    Returns:
        Dictionary with validation results
    """
    result = {
        "url": url,
        "reachable": False,
        "status_code": None,
        "content_length": 0,
        "proxy_count": 0,
        "format": "unknown",
        "protocol_guess": None,
        "sample_lines": [],
        "is_valid_source": False,
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, timeout=timeout)

        result["reachable"] = True
        result["status_code"] = resp.status_code

        if resp.status_code != 200:
            return result

        content = resp.text
        result["content_length"] = len(content)

        proxy_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}")
        matches = proxy_pattern.findall(content)
        result["proxy_count"] = len(matches)

        if matches:
            result["sample_lines"] = matches[:5]

            if content.strip().startswith("{") or content.strip().startswith("["):
                result["format"] = "json"
            elif "," in content and content.count(",") > content.count("\n"):
                result["format"] = "csv"
            elif "<table" in content.lower() or "<tr" in content.lower():
                result["format"] = "html_table"
            else:
                result["format"] = "plain_text"

            if "socks4" in url.lower() or "socks4" in content[:500].lower():
                result["protocol_guess"] = "socks4"
            elif "socks5" in url.lower() or "socks5" in content[:500].lower():
                result["protocol_guess"] = "socks5"
            else:
                result["protocol_guess"] = "http"

            result["is_valid_source"] = result["proxy_count"] >= 10

    except httpx.TimeoutException:
        result["error"] = "Request timeout"
    except httpx.HTTPError as e:
        result["error"] = f"HTTP error: {str(e)[:100]}"
    except Exception as e:
        result["error"] = f"Error: {str(e)[:100]}"

    return result


if __name__ == "__main__":
    app()
