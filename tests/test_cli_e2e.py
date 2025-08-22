"""CLI end-to-end tests.

Marked with the `e2e` pytest marker to keep separation from unit and
integration tests.
"""

# mypy: ignore-errors
import json

# Mark module as e2e tests
import pytest
from typer.testing import CliRunner

import proxywhirl.cli as cli
from proxywhirl import Scheme

pytestmark = pytest.mark.e2e


class _Anon:
    value = "elite"


class _Checked:
    def isoformat(self):
        return "2025-01-01T00:00:00Z"


class _ProxyLike:
    host = "h1"
    port = 8080
    schemes = [Scheme.HTTP]
    anonymity = _Anon()
    response_time = 0.1
    last_checked = _Checked()
    country_code = "US"

    # noqa: ARG002 below to ignore unused parameter in test stub
    def model_dump(self, mode: str | None = None) -> dict[str, object]:
        return {"host": str(self.host), "port": int(self.port)}


class FakePW:
    # noqa below to suppress doc and typing noise for a test stub
    def __init__(self, *args: object, **kwargs: object):  # noqa: D401, ANN002
        self._proxies = [_ProxyLike()]

    async def fetch_proxies(self, validate: bool | None = None) -> int:
        return len(self._proxies)

    def list_proxies(self) -> list[_ProxyLike]:
        return self._proxies

    async def validate_proxies(self) -> int:
        return len(self._proxies)

    async def get_proxy(self) -> _ProxyLike:
        return self._proxies[0]


def test_cli_fetch_list_validate_get(monkeypatch: pytest.MonkeyPatch):
    runner = CliRunner()
    monkeypatch.setattr(cli, "ProxyWhirl", FakePW)

    # fetch
    r = runner.invoke(cli.app, ["fetch", "--no-validate"])
    assert r.exit_code == 0

    # list in table
    r = runner.invoke(cli.app, ["list"])
    assert r.exit_code == 0 and "ProxyWhirl Proxies" in r.stdout

    # list json
    r = runner.invoke(cli.app, ["list", "--json"])
    assert r.exit_code == 0 and json.loads(r.stdout)[0]["host"] == "h1"

    # validate
    r = runner.invoke(cli.app, ["validate"])
    assert r.exit_code == 0

    # get formats
    r = runner.invoke(cli.app, ["get"])  # hostport
    assert r.exit_code == 0 and r.stdout.strip() == "h1:8080"
    r = runner.invoke(cli.app, ["get", "--format", "uri"])
    assert r.exit_code == 0 and r.stdout.strip() == "http://h1:8080"
    r = runner.invoke(cli.app, ["get", "--format", "json"])
    assert r.exit_code == 0 and json.loads(r.stdout)["host"] == "h1"
