"""Performance and load testing for the Notion Bot API."""

import asyncio
import time
import statistics
from typing import List, Dict
import httpx
import json


class LoadTester:
    """Load testing utility for API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize load tester."""
        self.base_url = base_url
        self.results: List[Dict] = []
        
    async def make_request(self, client: httpx.AsyncClient, method: str, path: str, **kwargs) -> Dict:
        """Make a single HTTP request and track metrics."""
        start_time = time.time()
        
        try:
            response = await client.request(method, f"{self.base_url}{path}", **kwargs)
            duration = time.time() - start_time
            
            return {
                "success": True,
                "status_code": response.status_code,
                "duration": duration,
                "error": None
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "status_code": None,
                "duration": duration,
                "error": str(e)
            }
    
    async def load_test_get_tasks(self, requests_per_second: int = 100, duration_seconds: int = 60):
        """
        Load test the GET /tasks endpoint.
        
        Args:
            requests_per_second: Target RPS
            duration_seconds: Test duration in seconds
        """
        print(f"\n{'='*60}")
        print(f"Load Test: GET /tasks")
        print(f"Target: {requests_per_second} req/s for {duration_seconds} seconds")
        print(f"{'='*60}\n")
        
        self.results = []
        total_requests = requests_per_second * duration_seconds
        delay_between_requests = 1.0 / requests_per_second
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()
            
            for i in range(total_requests):
                # Make request
                result = await self.make_request(client, "GET", "/tasks?limit=10")
                self.results.append(result)
                
                # Progress indicator
                if (i + 1) % requests_per_second == 0:
                    elapsed = time.time() - start_time
                    print(f"Progress: {i + 1}/{total_requests} requests ({elapsed:.1f}s elapsed)")
                
                # Rate limiting
                await asyncio.sleep(delay_between_requests)
        
        self._print_results()
    
    async def concurrent_test_create_tasks(self, concurrent_requests: int = 50):
        """
        Test concurrent task creation.
        
        Args:
            concurrent_requests: Number of simultaneous requests
        """
        print(f"\n{'='*60}")
        print(f"Concurrent Test: POST /tasks")
        print(f"Concurrent requests: {concurrent_requests}")
        print(f"{'='*60}\n")
        
        self.results = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create tasks to run concurrently
            tasks = []
            for i in range(concurrent_requests):
                task_data = {
                    "title": f"Load Test Task {i}",
                    "description": f"Created during load test at {time.time()}",
                    "status": "todo"
                }
                
                tasks.append(
                    self.make_request(
                        client,
                        "POST",
                        "/tasks",
                        json=task_data,
                        headers={"Content-Type": "application/json"}
                    )
                )
            
            # Execute all requests concurrently
            print(f"Sending {concurrent_requests} concurrent requests...")
            start_time = time.time()
            self.results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            print(f"Completed in {total_time:.2f} seconds")
        
        self._print_results()
    
    def _print_results(self):
        """Print test results and statistics."""
        if not self.results:
            print("No results to analyze")
            return
        
        # Calculate statistics
        successful_requests = [r for r in self.results if r["success"]]
        failed_requests = [r for r in self.results if not r["success"]]
        durations = [r["duration"] for r in successful_requests]
        
        total_requests = len(self.results)
        success_count = len(successful_requests)
        failure_count = len(failed_requests)
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        
        print(f"\n{'='*60}")
        print("Test Results")
        print(f"{'='*60}")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {success_count} ({success_rate:.2f}%)")
        print(f"Failed: {failure_count} ({100 - success_rate:.2f}%)")
        
        if durations:
            sorted_durations = sorted(durations)
            print(f"\nLatency Statistics:")
            print(f"  Min: {min(durations)*1000:.2f} ms")
            print(f"  Max: {max(durations)*1000:.2f} ms")
            print(f"  Mean: {statistics.mean(durations)*1000:.2f} ms")
            print(f"  Median (P50): {statistics.median(durations)*1000:.2f} ms")
            print(f"  P95: {sorted_durations[int(len(sorted_durations) * 0.95)]*1000:.2f} ms")
            print(f"  P99: {sorted_durations[int(len(sorted_durations) * 0.99)]*1000:.2f} ms")
            
            # Check if P95 meets target
            p95_ms = sorted_durations[int(len(sorted_durations) * 0.95)] * 1000
            if p95_ms < 500:
                print(f"\n✓ P95 latency target met ({p95_ms:.2f} ms < 500 ms)")
            else:
                print(f"\n✗ P95 latency target NOT met ({p95_ms:.2f} ms >= 500 ms)")
        
        # Status code distribution
        if successful_requests:
            status_codes = {}
            for r in successful_requests:
                code = r["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1
            
            print(f"\nStatus Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"  {code}: {count} ({count/success_count*100:.1f}%)")
        
        # Error summary
        if failed_requests:
            print(f"\nError Summary:")
            error_types = {}
            for r in failed_requests:
                error = r["error"]
                error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error}: {count}")
        
        print(f"{'='*60}\n")
    
    def passes_acceptance_criteria(self) -> bool:
        """
        Check if test results meet acceptance criteria.
        
        Returns:
            True if all criteria are met
        """
        if not self.results:
            return False
        
        successful_requests = [r for r in self.results if r["success"]]
        durations = [r["duration"] for r in successful_requests]
        
        # Criteria 1: No errors
        if len(successful_requests) != len(self.results):
            print("✗ FAILED: Errors detected during load test")
            return False
        
        # Criteria 2: P95 latency < 500ms
        if durations:
            sorted_durations = sorted(durations)
            p95_ms = sorted_durations[int(len(sorted_durations) * 0.95)] * 1000
            
            if p95_ms >= 500:
                print(f"✗ FAILED: P95 latency {p95_ms:.2f} ms >= 500 ms")
                return False
        
        print("✓ PASSED: All acceptance criteria met")
        return True


async def main():
    """Run all performance tests."""
    tester = LoadTester()
    
    # Test 1: Load test GET /tasks (100 req/s for 1 minute)
    print("\n" + "="*60)
    print("TEST 1: Load Test - GET /tasks")
    print("="*60)
    await tester.load_test_get_tasks(requests_per_second=100, duration_seconds=60)
    
    test1_passed = tester.passes_acceptance_criteria()
    
    # Wait before next test
    print("\nWaiting 10 seconds before next test...")
    await asyncio.sleep(10)
    
    # Test 2: Concurrent task creation (50 simultaneous requests)
    print("\n" + "="*60)
    print("TEST 2: Concurrent Task Creation")
    print("="*60)
    await tester.concurrent_test_create_tasks(concurrent_requests=50)
    
    test2_passed = tester.passes_acceptance_criteria()
    
    # Final summary
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Load Test): {'PASSED ✓' if test1_passed else 'FAILED ✗'}")
    print(f"Test 2 (Concurrent): {'PASSED ✓' if test2_passed else 'FAILED ✗'}")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("\n✓ All performance tests PASSED")
        return 0
    else:
        print("\n✗ Some performance tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
