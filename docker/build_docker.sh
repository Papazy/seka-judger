#!/bin/bash
set -ex

# Check if --no-cache flag is provided
PLATFORM="linux/amd64"
NO_CACHE=""
if [ "$1" == "--no-cache" ]; then
    NO_CACHE="--no-cache"
    echo "Building with --no-cache flag..."
fi

docker buildx build $NO_CACHE --platform $PLATFORM -f python_runner.dockerfile -t seka-python-runner:latest .
docker buildx build $NO_CACHE --platform $PLATFORM -f c_runner.dockerfile -t seka-c-runner:latest .
docker buildx build $NO_CACHE --platform $PLATFORM -f cpp_runner.dockerfile -t seka-cpp-runner:latest .
docker buildx build $NO_CACHE --platform $PLATFORM -f java_runner.dockerfile -t seka-java-runner:latest .
