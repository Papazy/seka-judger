#!/bin/bash
set -ex

# Check if --no-cache flag is provided
NO_CACHE=""
if [ "$1" == "--no-cache" ]; then
    NO_CACHE="--no-cache"
    echo "Building with --no-cache flag..."
fi

docker build $NO_CACHE -f python_runner.dockerfile -t seka-python-runner:latest .
docker build $NO_CACHE -f c_runner.dockerfile -t seka-c-runner:latest .
docker build $NO_CACHE -f cpp_runner.dockerfile -t seka-cpp-runner:latest .
docker build $NO_CACHE -f java_runner.dockerfile -t seka-java-runner:latest .
