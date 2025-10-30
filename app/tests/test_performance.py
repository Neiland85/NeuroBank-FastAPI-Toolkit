"""
Performance tests for NeuroBank FastAPI Toolkit

These tests validate that our performance optimizations are effective.
"""
import time

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.auth.dependencies import get_api_key
from app.config import get_settings


class TestImportPerformance:
    """Test that imports and module loading are optimized"""

    def test_no_duplicate_imports(self):
        """Ensure main.py doesn't have duplicate imports"""
        with open("app/main.py", "r") as f:
            content = f.read()
            # Check that datetime is only imported once at the top
            import_lines = [
                line for line in content.split("\n") if line.startswith("import datetime")
            ]
            assert (
                len(import_lines) == 0
            ), "Found standalone 'import datetime' - should use 'from datetime import ...'"

            # Check for duplicate imports within functions
            assert (
                "    import datetime" not in content
            ), "Found datetime import inside function"
            assert "    import os" not in content, "Found os import inside function"


class TestCachedSettings:
    """Test that settings and API key are properly cached"""

    def test_api_key_caching(self):
        """Test that get_api_key returns cached value"""
        # Clear the cache first
        get_api_key.cache_clear()

        # First call
        start = time.perf_counter()
        key1 = get_api_key()
        first_call_time = time.perf_counter() - start

        # Second call (should be cached)
        start = time.perf_counter()
        key2 = get_api_key()
        second_call_time = time.perf_counter() - start

        # Cached call should be much faster
        assert key1 == key2, "API keys should match"
        assert (
            second_call_time < first_call_time * 0.5
        ), "Cached call should be at least 2x faster"

    def test_settings_caching(self):
        """Test that get_settings returns cached value"""
        # Clear the cache first
        get_settings.cache_clear()

        # First call
        start = time.perf_counter()
        settings1 = get_settings()
        first_call_time = time.perf_counter() - start

        # Second call (should be cached)
        start = time.perf_counter()
        settings2 = get_settings()
        second_call_time = time.perf_counter() - start

        # Should return same instance
        assert settings1 is settings2, "Should return same cached instance"
        # Cached call should be much faster
        assert (
            second_call_time < first_call_time * 0.5
        ), "Cached call should be at least 2x faster"


class TestBackofficePerformance:
    """Test backoffice endpoint performance"""

    @pytest.mark.asyncio
    async def test_transaction_search_performance(self):
        """Test that transaction search endpoint performs efficiently"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Warm up
            await ac.get("/backoffice/api/transactions/search?page_size=10")

            # Test with larger page size
            start = time.perf_counter()
            response = await ac.get("/backoffice/api/transactions/search?page_size=100")
            elapsed = time.perf_counter() - start

            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) > 0

            # Should complete in reasonable time even with 100 items
            assert elapsed < 0.5, f"Transaction search took {elapsed:.3f}s, should be < 0.5s"

    @pytest.mark.asyncio
    async def test_metrics_endpoint_performance(self):
        """Test that metrics endpoint responds quickly"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Measure multiple calls
            times = []
            for _ in range(5):
                start = time.perf_counter()
                response = await ac.get("/backoffice/api/metrics")
                elapsed = time.perf_counter() - start
                times.append(elapsed)

                assert response.status_code == 200

            # Average response time should be very fast
            avg_time = sum(times) / len(times)
            assert avg_time < 0.1, f"Average metrics call took {avg_time:.3f}s, should be < 0.1s"


class TestAPIEndpointPerformance:
    """Test main API endpoint performance"""

    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """Test that health check is fast"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # Measure multiple calls
            times = []
            for _ in range(10):
                start = time.perf_counter()
                response = await ac.get("/health")
                elapsed = time.perf_counter() - start
                times.append(elapsed)

                assert response.status_code == 200

            # Average response time should be very fast
            avg_time = sum(times) / len(times)
            assert avg_time < 0.05, f"Average health check took {avg_time:.3f}s, should be < 0.05s"

    @pytest.mark.asyncio
    async def test_root_endpoint_performance(self):
        """Test that root endpoint is fast"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            start = time.perf_counter()
            response = await ac.get("/")
            elapsed = time.perf_counter() - start

            assert response.status_code == 200
            assert elapsed < 0.05, f"Root endpoint took {elapsed:.3f}s, should be < 0.05s"
