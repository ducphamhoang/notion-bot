# Performance Testing

This directory contains performance and load testing scripts for the Notion Bot API.

## Test Scenarios

### 1. Load Test - GET /tasks

**Objective**: Verify the API can handle sustained high load.

**Test Parameters**:
- **Rate**: 100 requests per second
- **Duration**: 60 seconds
- **Total Requests**: 6,000

**Acceptance Criteria**:
- ✓ P95 latency < 500ms
- ✓ No errors during test
- ✓ All requests return 200 status

### 2. Concurrent Task Creation

**Objective**: Test the API under concurrent write operations.

**Test Parameters**:
- **Concurrent Requests**: 50 simultaneous POST requests
- **Operation**: Create new tasks

**Acceptance Criteria**:
- ✓ All requests complete successfully
- ✓ No errors or timeouts
- ✓ P95 latency < 500ms

## Running Performance Tests

### Prerequisites

1. **Start the API**:
   ```bash
   docker-compose up -d
   ```

2. **Verify API is healthy**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install httpx
   ```

### Run All Tests

```bash
./scripts/run_performance_tests.sh
```

### Run Individual Tests

```bash
# Run Python test script directly
python tests/performance/load_test.py
```

## Test Results

### Example Output

```
==============================
Test Results
==============================
Total Requests: 6000
Successful: 6000 (100.00%)
Failed: 0 (0.00%)

Latency Statistics:
  Min: 12.45 ms
  Max: 456.78 ms
  Mean: 87.23 ms
  Median (P50): 76.45 ms
  P95: 234.56 ms
  P99: 345.67 ms

✓ P95 latency target met (234.56 ms < 500 ms)

Status Code Distribution:
  200: 6000 (100.0%)
```

## Interpreting Results

### Latency Percentiles

- **P50 (Median)**: Half of all requests complete faster than this
- **P95**: 95% of requests complete faster than this (most important for SLA)
- **P99**: 99% of requests complete faster than this

### Target Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| P95 Latency | < 500ms | 95% of requests should complete in under 500ms |
| Error Rate | 0% | No errors during sustained load |
| Throughput | 100 req/s | Sustained rate of 100 requests per second |

### Common Issues

#### High Latency

If P95 > 500ms:

1. **Check database performance**:
   - Add missing indexes
   - Optimize queries
   - Check connection pool size

2. **Check resource usage**:
   - CPU usage > 80%
   - Memory usage > 80%
   - Disk I/O bottleneck

3. **Check Notion API**:
   - Rate limit hits
   - Slow Notion responses
   - Network latency

#### Request Errors

If error rate > 0%:

1. **Check application logs**:
   ```bash
   docker-compose logs api
   ```

2. **Check database connectivity**:
   ```bash
   docker-compose logs mongodb
   ```

3. **Check resource limits**:
   - Container memory limits
   - Connection pool exhaustion
   - File descriptor limits

## Continuous Performance Testing

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: |
          sleep 10
          curl --retry 10 --retry-delay 5 http://localhost:8000/health
      
      - name: Run performance tests
        run: ./scripts/run_performance_tests.sh
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: performance-results
          path: test-results/
```

### Monitoring Performance Over Time

Track performance metrics over time:

```bash
# Save results with timestamp
timestamp=$(date +%Y%m%d_%H%M%S)
./scripts/run_performance_tests.sh > "results/perf_${timestamp}.txt"
```

Compare with previous runs:

```bash
# Compare P95 latencies
grep "P95:" results/*.txt
```

## Load Testing Best Practices

1. **Start small**: Begin with lower load and gradually increase
2. **Monitor resources**: Watch CPU, memory, disk I/O during tests
3. **Test realistic scenarios**: Use production-like data and traffic patterns
4. **Run multiple times**: Performance can vary, run tests 3-5 times
5. **Test from different locations**: Network latency varies by geography
6. **Test peak loads**: Test at 2-3x expected peak traffic
7. **Long-running tests**: Run extended tests (24+ hours) to find memory leaks

## Advanced Testing

### Custom Load Patterns

Modify `load_test.py` to test different scenarios:

```python
# Ramp-up test
await tester.load_test_get_tasks(
    requests_per_second=10,  # Start slow
    duration_seconds=300     # 5 minutes
)

# Spike test
await tester.load_test_get_tasks(
    requests_per_second=500,  # High spike
    duration_seconds=10       # Short duration
)
```

### Stress Testing

Find the breaking point:

```python
# Gradually increase load until failures occur
for rps in [50, 100, 200, 500, 1000]:
    print(f"\nTesting at {rps} req/s...")
    await tester.load_test_get_tasks(
        requests_per_second=rps,
        duration_seconds=30
    )
    
    if not tester.passes_acceptance_criteria():
        print(f"Breaking point: {rps} req/s")
        break
```

## Resources

- [API Documentation](../docs/API_DOCUMENTATION.md)
- [Operations Runbook](../docs/OPERATIONS_RUNBOOK.md)
- [Performance Tuning Guide](../docs/OPERATIONS_RUNBOOK.md#performance-tuning)
