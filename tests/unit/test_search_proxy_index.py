"""Tests for proxy search index system."""

from proxywhirl.search_proxy_index import ProxySearchEngine, SearchIndex


class TestSearchIndex:
    """Test SearchIndex class."""

    def test_index_creation(self):
        """Test index creation."""
        index = SearchIndex(name="proxy_index", indexed_fields=["ip", "port"])
        assert index.name == "proxy_index"
        assert len(index.indexed_fields) == 2


class TestProxySearchEngine:
    """Test ProxySearchEngine class."""

    def test_create_index(self):
        """Test creating index."""
        engine = ProxySearchEngine()
        assert engine.create_index("proxy_index", ["ip", "port", "country"])

    def test_create_duplicate_index(self):
        """Test creating duplicate index."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip", "port"])
        assert not engine.create_index("proxy_index", ["ip", "port"])

    def test_index_document(self):
        """Test indexing document."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip", "port", "country"])
        doc = {"ip": "192.168.1.1", "port": 8080, "country": "US"}
        assert engine.index_document("proxy_index", "doc1", doc)

    def test_index_document_missing_index(self):
        """Test indexing to missing index."""
        engine = ProxySearchEngine()
        doc = {"ip": "192.168.1.1", "port": 8080}
        assert not engine.index_document("missing", "doc1", doc)

    def test_search(self):
        """Test searching documents."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip", "country"])
        doc1 = {"ip": "192.168.1.1", "country": "United States"}
        doc2 = {"ip": "10.0.0.1", "country": "Canada"}
        engine.index_document("proxy_index", "doc1", doc1)
        engine.index_document("proxy_index", "doc2", doc2)

        results = engine.search("united")
        assert len(results) > 0

    def test_search_exact_match(self):
        """Test exact search match."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip"])
        doc = {"ip": "192.168.1.1"}
        engine.index_document("proxy_index", "doc1", doc)

        results = engine.search("192")
        assert "proxy_index:doc1" in results

    def test_delete_document(self):
        """Test deleting document."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip"])
        doc = {"ip": "192.168.1.1"}
        engine.index_document("proxy_index", "doc1", doc)
        assert engine.delete_document("doc1")
        assert "proxy_index:doc1" not in engine.search("192")

    def test_get_statistics(self):
        """Test getting statistics."""
        engine = ProxySearchEngine()
        engine.create_index("proxy_index", ["ip"])
        doc = {"ip": "192.168.1.1"}
        engine.index_document("proxy_index", "doc1", doc)
        stats = engine.get_statistics()
        assert stats["indices"] == 1
        assert stats["indexed_items"] == 1

    def test_tokenization(self):
        """Test text tokenization."""
        engine = ProxySearchEngine()
        tokens = engine._tokenize("Test String With Numbers 123")
        assert "test" in tokens
        assert "string" in tokens
        assert "with" in tokens
