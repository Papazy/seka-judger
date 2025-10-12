#!/bin/bash

# Script untuk build semua Docker images untuk SEKA Judger
# Author: SEKA Judger Team
# Date: 2025-10-11

set -e  # Exit on error

echo "🚀 Building SEKA Judger Docker Images..."
echo "========================================"

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to build image
build_image() {
    local dockerfile=$1
    local image_name=$2
    
    echo -e "\n${BLUE}📦 Building $image_name...${NC}"
    
    if docker build -f "docker/$dockerfile" -t "$image_name" .; then
        echo -e "${GREEN}✅ Successfully built $image_name${NC}"
    else
        echo -e "${RED}❌ Failed to build $image_name${NC}"
        exit 1
    fi
}

# Build all images
build_image "c_runner.dockerfile" "seka-judger-c:latest"
build_image "cpp_runner.dockerfile" "seka-judger-cpp:latest"
build_image "java_runner.dockerfile" "seka-judger-java:latest"
build_image "python_runner.dockerfile" "seka-judger-python:latest"

echo ""
echo "========================================"
echo -e "${GREEN}✅ All images built successfully!${NC}"
echo ""
echo "📋 Built images:"
docker images | grep seka-judger

echo ""
echo -e "${BLUE}🎯 Next steps:${NC}"
echo "1. Install Docker SDK: pip install docker"
echo "2. Update judge_engine.py to use DockerExecutor"
echo "3. Test the system: python -m uvicorn main:app --reload"
echo ""
