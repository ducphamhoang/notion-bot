"""Metrics collection and monitoring for the Notion Bot API."""

import time
from typing import Dict, List
from collections import defaultdict, deque
import asyncio
from datetime import datetime, timedelta
import statistics


class MetricsCollector:
    """In-memory metrics collector for API monitoring."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._request_durations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._status_codes: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._notion_api_calls: int = 0
        self._rate_limit_hits: int = 0
        self._lock = asyncio.Lock()
        
    async def record_request_duration(self, endpoint: str, duration: float):
        """Record request duration for an endpoint."""
        async with self._lock:
            self._request_durations[endpoint].append(duration)
    
    async def record_status_code(self, endpoint: str, status_code: int):
        """Record HTTP status code for an endpoint."""
        async with self._lock:
            self._status_codes[endpoint][status_code] += 1
    
    async def increment_notion_api_calls(self):
        """Increment Notion API call counter."""
        async with self._lock:
            self._notion_api_calls += 1
    
    async def increment_rate_limit_hits(self):
        """Increment rate limit hit counter."""
        async with self._lock:
            self._rate_limit_hits += 1
    
    async def get_duration_percentiles(self, endpoint: str) -> Dict[str, float]:
        """Get duration percentiles (P50, P95, P99) for an endpoint."""
        async with self._lock:
            durations = list(self._request_durations.get(endpoint, []))
            
            if not durations:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
            
            sorted_durations = sorted(durations)
            
            return {
                "p50": statistics.median(sorted_durations),
                "p95": sorted_durations[int(len(sorted_durations) * 0.95)] if len(sorted_durations) > 1 else sorted_durations[0],
                "p99": sorted_durations[int(len(sorted_durations) * 0.99)] if len(sorted_durations) > 1 else sorted_durations[0],
                "count": len(durations)
            }
    
    async def get_status_codes(self, endpoint: str) -> Dict[int, int]:
        """Get status code counts for an endpoint."""
        async with self._lock:
            return dict(self._status_codes.get(endpoint, {}))
    
    async def get_all_metrics(self) -> dict:
        """Get all collected metrics."""
        async with self._lock:
            # Collect duration stats for all endpoints
            duration_stats = {}
            for endpoint in self._request_durations.keys():
                durations = list(self._request_durations[endpoint])
                if durations:
                    sorted_durations = sorted(durations)
                    duration_stats[endpoint] = {
                        "p50": statistics.median(sorted_durations),
                        "p95": sorted_durations[int(len(sorted_durations) * 0.95)] if len(sorted_durations) > 1 else sorted_durations[0],
                        "p99": sorted_durations[int(len(sorted_durations) * 0.99)] if len(sorted_durations) > 1 else sorted_durations[0],
                        "count": len(durations),
                        "mean": statistics.mean(durations)
                    }
            
            return {
                "request_duration_seconds": duration_stats,
                "http_status_codes": dict(self._status_codes),
                "notion_api_calls_total": self._notion_api_calls,
                "rate_limit_hits_total": self._rate_limit_hits
            }
    
    async def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus text format."""
        metrics = await self.get_all_metrics()
        lines = []
        
        # Request duration metrics
        lines.append("# HELP http_request_duration_seconds HTTP request duration in seconds")
        lines.append("# TYPE http_request_duration_seconds summary")
        
        for endpoint, stats in metrics["request_duration_seconds"].items():
            endpoint_label = endpoint.replace('"', '\\"')
            lines.append(f'http_request_duration_seconds{{endpoint="{endpoint_label}",quantile="0.5"}} {stats["p50"]:.6f}')
            lines.append(f'http_request_duration_seconds{{endpoint="{endpoint_label}",quantile="0.95"}} {stats["p95"]:.6f}')
            lines.append(f'http_request_duration_seconds{{endpoint="{endpoint_label}",quantile="0.99"}} {stats["p99"]:.6f}')
            lines.append(f'http_request_duration_seconds_sum{{endpoint="{endpoint_label}"}} {stats["mean"] * stats["count"]:.6f}')
            lines.append(f'http_request_duration_seconds_count{{endpoint="{endpoint_label}"}} {stats["count"]}')
        
        # HTTP status codes
        lines.append("")
        lines.append("# HELP http_requests_total Total number of HTTP requests by endpoint and status code")
        lines.append("# TYPE http_requests_total counter")
        
        for endpoint, codes in metrics["http_status_codes"].items():
            endpoint_label = endpoint.replace('"', '\\"')
            for status_code, count in codes.items():
                lines.append(f'http_requests_total{{endpoint="{endpoint_label}",status_code="{status_code}"}} {count}')
        
        # Notion API calls
        lines.append("")
        lines.append("# HELP notion_api_calls_total Total number of Notion API calls")
        lines.append("# TYPE notion_api_calls_total counter")
        lines.append(f'notion_api_calls_total {metrics["notion_api_calls_total"]}')
        
        # Rate limit hits
        lines.append("")
        lines.append("# HELP rate_limit_hits_total Total number of rate limit hits")
        lines.append("# TYPE rate_limit_hits_total counter")
        lines.append(f'rate_limit_hits_total {metrics["rate_limit_hits_total"]}')
        
        return "\n".join(lines) + "\n"


# Global metrics collector instance
_metrics_collector: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


class HealthCheckCache:
    """Cache for health check results to avoid excessive checks."""
    
    def __init__(self, ttl_seconds: int = 30):
        """Initialize health check cache with TTL."""
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple] = {}  # key -> (result, timestamp)
        self._lock = asyncio.Lock()
    
    async def get(self, key: str):
        """Get cached result if not expired."""
        async with self._lock:
            if key in self._cache:
                result, timestamp = self._cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    return result
            return None
    
    async def set(self, key: str, result):
        """Set cached result with current timestamp."""
        async with self._lock:
            self._cache[key] = (result, datetime.now())


# Global health check cache instance
_health_cache: HealthCheckCache = None


def get_health_cache() -> HealthCheckCache:
    """Get global health check cache instance."""
    global _health_cache
    if _health_cache is None:
        _health_cache = HealthCheckCache(ttl_seconds=30)
    return _health_cache
