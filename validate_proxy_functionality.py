#!/usr/bin/env python3
"""
ProxyWhirl Loader Functionality Validator
========================================

This script tests whether each loader actually returns working, functional proxies
by making real HTTP requests through them. This is a practical test of loader
effectiveness beyond just code validation.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional

import httpx
from loguru import logger

from proxywhirl.loaders import (
    ClarketmHttpLoader,
    FreshProxyListLoader,
    MonosansLoader,
    OpenProxySpaceLoader,
    ProxyNovaLoader,
    ProxyScrapeLoader,
    TheSpeedXHttpLoader,
    TheSpeedXSocksLoader,
)


@dataclass
class LoaderTestResult:
    """Results from testing a proxy loader."""
    name: str
    success: bool
    error_message: Optional[str] = None
    proxy_count: int = 0
    working_proxies: int = 0
    avg_response_time: Optional[float] = None
    test_sample_size: int = 0


@dataclass
class ProxyTestResult:
    """Results from testing an individual proxy."""
    proxy: str
    working: bool
    response_time: Optional[float] = None
    error: Optional[str] = None


class ProxyFunctionalityValidator:
    """Validates that proxy loaders return working proxies."""
    
    def __init__(self, max_proxies_to_test: int = 5, timeout: int = 10):
        """
        Initialize the validator.
        
        Args:
            max_proxies_to_test: Maximum number of proxies to test per loader
            timeout: Timeout for proxy requests in seconds
        """
        self.max_proxies_to_test = max_proxies_to_test
        self.timeout = timeout
        self.test_url = "http://httpbin.org/ip"  # Simple endpoint to test proxy functionality
        
        # Define all loaders to test
        self.loaders = [
            ("FreshProxyListLoader", FreshProxyListLoader),
            ("TheSpeedXHttpLoader", TheSpeedXHttpLoader),
            ("TheSpeedXSocksLoader", TheSpeedXSocksLoader), 
            ("ClarketmHttpLoader", ClarketmHttpLoader),
            ("MonosansLoader", MonosansLoader),
            ("ProxyScrapeLoader", ProxyScrapeLoader),
            ("ProxyNovaLoader", ProxyNovaLoader),
            ("OpenProxySpaceLoader", OpenProxySpaceLoader),
            # Skip UserProvidedLoader since it requires input data
        ]

    async def test_proxy(self, proxy_url: str) -> ProxyTestResult:
        """Test if a single proxy is working."""
        start_time = time.time()
        
        try:
            # Parse proxy URL
            if "://" not in proxy_url:
                proxy_url = f"http://{proxy_url}"
                
            async with httpx.AsyncClient(
                proxies={"http://": proxy_url, "https://": proxy_url},
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(self.test_url)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return ProxyTestResult(
                        proxy=proxy_url,
                        working=True,
                        response_time=response_time
                    )
                else:
                    return ProxyTestResult(
                        proxy=proxy_url,
                        working=False,
                        error=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            return ProxyTestResult(
                proxy=proxy_url,
                working=False,
                error=str(e)
            )

    async def test_loader(self, name: str, loader_class) -> LoaderTestResult:
        """Test a single proxy loader."""
        logger.info(f"Testing {name}...")
        
        try:
            # Instantiate the loader
            loader = loader_class()
            
            # Load proxies
            logger.info(f"Loading proxies from {name}...")
            df = await asyncio.get_event_loop().run_in_executor(None, loader.load)
            
            if df.empty:
                return LoaderTestResult(
                    name=name,
                    success=False,
                    error_message="No proxies returned",
                    proxy_count=0
                )
            
            proxy_count = len(df)
            logger.info(f"{name} returned {proxy_count} proxies")
            
            # Test a sample of proxies
            sample_size = min(self.max_proxies_to_test, proxy_count)
            sample_df = df.head(sample_size)
            
            # Convert proxy data to URLs for testing
            proxy_urls = []
            for _, row in sample_df.iterrows():
                # Handle different column naming conventions
                host = row.get('host') or row.get('ip')
                port = row.get('port')
                scheme = row.get('protocol', row.get('scheme', 'http')).lower()
                
                if host and port:
                    proxy_url = f"{scheme}://{host}:{port}"
                    proxy_urls.append(proxy_url)
            
            if not proxy_urls:
                return LoaderTestResult(
                    name=name,
                    success=False,
                    error_message="Could not format proxies for testing",
                    proxy_count=proxy_count
                )
            
            # Test proxies concurrently
            logger.info(f"Testing {len(proxy_urls)} proxies from {name}...")
            test_results = await asyncio.gather(
                *[self.test_proxy(url) for url in proxy_urls],
                return_exceptions=True
            )
            
            # Analyze results
            working_count = 0
            total_response_time = 0
            valid_responses = 0
            
            for result in test_results:
                if isinstance(result, ProxyTestResult):
                    if result.working:
                        working_count += 1
                        if result.response_time:
                            total_response_time += result.response_time
                            valid_responses += 1
            
            avg_response_time = total_response_time / valid_responses if valid_responses > 0 else None
            
            return LoaderTestResult(
                name=name,
                success=True,
                proxy_count=proxy_count,
                working_proxies=working_count,
                avg_response_time=avg_response_time,
                test_sample_size=len(proxy_urls)
            )
            
        except Exception as e:
            logger.error(f"Error testing {name}: {e}")
            return LoaderTestResult(
                name=name,
                success=False,
                error_message=str(e)
            )

    async def validate_all_loaders(self) -> List[LoaderTestResult]:
        """Test all proxy loaders."""
        logger.info("Starting proxy functionality validation...")
        results = []
        
        for name, loader_class in self.loaders:
            try:
                result = await self.test_loader(name, loader_class)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to test {name}: {e}")
                results.append(LoaderTestResult(
                    name=name,
                    success=False,
                    error_message=f"Test execution failed: {e}"
                ))
        
        return results

    def print_results(self, results: List[LoaderTestResult]):
        """Print formatted results."""
        print("\n" + "="*80)
        print("🔍 PROXYWHIRL LOADER FUNCTIONALITY VALIDATION REPORT")
        print("="*80)
        
        working_loaders = [r for r in results if r.success and r.working_proxies > 0]
        partially_working = [r for r in results if r.success and r.proxy_count > 0 and r.working_proxies == 0]
        failed_loaders = [r for r in results if not r.success]
        
        print("\n📊 SUMMARY:")
        print(f"   ✅ Fully Working Loaders: {len(working_loaders)}")
        print(f"   ⚠️  Loaders with Non-Working Proxies: {len(partially_working)}")  
        print(f"   ❌ Failed Loaders: {len(failed_loaders)}")
        
        if working_loaders:
            print("\n✅ WORKING LOADERS (return functional proxies):")
            for result in sorted(working_loaders, key=lambda x: x.working_proxies, reverse=True):
                success_rate = (result.working_proxies / result.test_sample_size) * 100
                avg_time_str = f"{result.avg_response_time:.2f}s" if result.avg_response_time else "N/A"
                print(f"   • {result.name}:")
                print(f"     - Total proxies: {result.proxy_count}")
                print(f"     - Working proxies: {result.working_proxies}/{result.test_sample_size} ({success_rate:.1f}%)")
                print(f"     - Avg response time: {avg_time_str}")
        
        if partially_working:
            print("\n⚠️  LOADERS WITH NON-WORKING PROXIES:")
            for result in partially_working:
                print(f"   • {result.name}:")
                print(f"     - Total proxies: {result.proxy_count}")
                print(f"     - Working proxies: 0/{result.test_sample_size} (0%)")
                print("     - Issue: Proxies returned but none are functional")
        
        if failed_loaders:
            print("\n❌ FAILED LOADERS:")
            for result in failed_loaders:
                print(f"   • {result.name}: {result.error_message}")
        
        print("\n" + "="*80)


async def main():
    """Main execution function."""
    validator = ProxyFunctionalityValidator(max_proxies_to_test=3, timeout=15)
    results = await validator.validate_all_loaders()
    validator.print_results(results)


if __name__ == "__main__":
    asyncio.run(main())
