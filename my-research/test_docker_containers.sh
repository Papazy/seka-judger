#!/bin/bash

# Quick test script untuk Docker containers
# Test manual setiap container sebelum integrasi dengan API

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "🧪 Testing SEKA Judger Docker Containers"
echo "========================================="

# Function to test a container
test_container() {
    local lang=$1
    local image=$2
    local filename=$3
    local code=$4
    local input=$5
    local expected=$6
    
    echo -e "\n${BLUE}Testing $lang container...${NC}"
    
    # Create temp directory
    TEST_DIR="/tmp/seka_test_${lang}_$$"
    mkdir -p "$TEST_DIR"
    
    # Write files
    echo "$code" > "$TEST_DIR/$filename"
    echo "$input" > "$TEST_DIR/input.txt"
    
    # Run container
    if docker run --rm \
        -v "$TEST_DIR:/code" \
        --network none \
        --memory=256m \
        "$image" 2>&1; then
        
        # Check output
        if [ -f "$TEST_DIR/output.txt" ]; then
            actual=$(cat "$TEST_DIR/output.txt")
            if [ "$actual" = "$expected" ]; then
                echo -e "${GREEN}✅ $lang test PASSED (output: $actual)${NC}"
            else
                echo -e "${RED}❌ $lang test FAILED${NC}"
                echo "Expected: $expected"
                echo "Got: $actual"
            fi
        else
            echo -e "${RED}❌ $lang test FAILED - no output file${NC}"
            if [ -f "$TEST_DIR/error.txt" ]; then
                echo "Error: $(cat $TEST_DIR/error.txt)"
            fi
        fi
    else
        echo -e "${RED}❌ $lang container failed to run${NC}"
    fi
    
    # Cleanup
    rm -rf "$TEST_DIR"
}

# Test C
C_CODE='#include <stdio.h>
int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}'
test_container "C" "seka-judger-c:latest" "main.c" "$C_CODE" "5 10" "15"

# Test C++
CPP_CODE='#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b;
    return 0;
}'
test_container "C++" "seka-judger-cpp:latest" "main.cpp" "$CPP_CODE" "7 3" "10"

# Test Java
JAVA_CODE='import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.print(a + b);
    }
}'
test_container "Java" "seka-judger-java:latest" "Main.java" "$JAVA_CODE" "12 8" "20"

# Test Python
PYTHON_CODE='a, b = map(int, input().split())
print(a + b, end="")'
test_container "Python" "seka-judger-python:latest" "main.py" "$PYTHON_CODE" "15 25" "40"

echo ""
echo "========================================="
echo -e "${GREEN}🎉 All tests completed!${NC}"
