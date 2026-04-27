"""Full-text search system for proxy metadata.

Implements indexed search over proxy attributes,
source information, and custom tags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class SearchIndex:
    """Represents a search index."""

    name: str
    indexed_fields: list[str] = field(default_factory=list)
    indexed_items: int = 0
    created_at: int = field(default_factory=lambda: int(__import__("time").time()))

    def __repr__(self) -> str:
        return f"Index({self.name}, fields={len(self.indexed_fields)})"


class ProxySearchEngine:
    """Full-text search engine for proxy metadata."""

    def __init__(self) -> None:
        """Initialize search engine."""
        self._indices: dict[str, SearchIndex] = {}
        self._inverted_index: dict[str, set[str]] = {}
        logger.debug("ProxySearchEngine initialized")

    def create_index(self, name: str, fields: list[str]) -> bool:
        """Create a search index.

        Args:
            name: Index name
            fields: Fields to index

        Returns:
            True if created
        """
        if name in self._indices:
            logger.warning(f"Index already exists: {name}")
            return False

        index = SearchIndex(name=name, indexed_fields=fields)
        self._indices[name] = index
        logger.info(f"Search index created: {name}")
        return True

    def index_document(self, index_name: str, doc_id: str, document: dict[str, Any]) -> bool:
        """Index a document.

        Args:
            index_name: Index name
            doc_id: Document ID
            document: Document to index

        Returns:
            True if indexed
        """
        if index_name not in self._indices:
            logger.warning(f"Index not found: {index_name}")
            return False

        index = self._indices[index_name]

        for field in index.indexed_fields:
            if field not in document:
                continue

            value = str(document[field]).lower()
            tokens = self._tokenize(value)

            for token in tokens:
                if token not in self._inverted_index:
                    self._inverted_index[token] = set()
                self._inverted_index[token].add(f"{index_name}:{doc_id}")

        index.indexed_items += 1
        logger.debug(f"Document indexed: {doc_id}")
        return True

    def search(self, query: str, index_name: str = "") -> set[str]:
        """Search documents.

        Args:
            query: Search query
            index_name: Optional index name to limit search

        Returns:
            Set of matching document IDs
        """
        tokens = self._tokenize(query)
        if not tokens:
            return set()

        results: set[str] | None = None

        for token in tokens:
            matches = self._inverted_index.get(token, set())

            if index_name:
                matches = {doc_id for doc_id in matches if doc_id.startswith(f"{index_name}:")}

            if results is None:
                results = matches.copy()
            else:
                results &= matches

        return results or set()

    def search_range(self, field_name: str, min_val: Any, max_val: Any) -> set[str]:
        """Search within a range (for numeric fields).

        Args:
            field_name: Field to search
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Set of matching document IDs
        """
        results: set[str] = set()

        for token, doc_ids in self._inverted_index.items():
            try:
                val = float(token)
                if min_val <= val <= max_val:
                    results.update(doc_ids)
            except ValueError:
                continue

        return results

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from indices.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted
        """
        found = False
        for token_docs in self._inverted_index.values():
            if doc_id in token_docs:
                token_docs.discard(doc_id)
                found = True

        if found:
            logger.debug(f"Document deleted: {doc_id}")

        return found

    def get_statistics(self) -> dict[str, Any]:
        """Get search engine statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            "indices": len(self._indices),
            "indexed_items": sum(idx.indexed_items for idx in self._indices.values()),
            "unique_tokens": len(self._inverted_index),
            "average_docs_per_token": (
                sum(len(docs) for docs in self._inverted_index.values()) / len(self._inverted_index)
                if self._inverted_index
                else 0
            ),
        }

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text for indexing.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 2]
