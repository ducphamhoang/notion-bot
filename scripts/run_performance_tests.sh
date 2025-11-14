#!/bin/bash
set -e

echo "======================================================"
echo "Notion Bot API - Performance Testing Suite"
echo "======================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API is running
echo "Checking if API is running..."
if ! curl -f -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}ERROR: API is not running or not healthy${NC}"
    echo "Please start the API with: docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}✓ API is running${NC}"
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: Must run from project root${NC}"
    exit 1
fi

# Install required packages if not already installed
echo "Checking dependencies..."
if ! python -c "import httpx" 2>/dev/null; then
    echo "Installing httpx..."
    pip install httpx
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Create some test data first
echo "Setting up test data..."
for i in {1..20}; do
    curl -s -X POST http://localhost:8000/tasks \
        -H "Content-Type: application/json" \
        -d "{\"title\": \"Test Task $i\", \"status\": \"todo\"}" > /dev/null
done
echo -e "${GREEN}✓ Test data created${NC}"
echo ""

# Run performance tests
echo "Starting performance tests..."
echo ""

python tests/performance/load_test.py

EXIT_CODE=$?

echo ""
echo "======================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Performance tests PASSED ✓${NC}"
else
    echo -e "${RED}Performance tests FAILED ✗${NC}"
fi
echo "======================================================"
echo ""

# Check metrics endpoint
echo "Fetching current metrics..."
curl -s http://localhost:8000/metrics | grep -E "(http_request_duration|http_requests_total|notion_api_calls|rate_limit_hits)" | head -20

echo ""
echo "Full metrics available at: http://localhost:8000/metrics"
echo ""

exit $EXIT_CODE
