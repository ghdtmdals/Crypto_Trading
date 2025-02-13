#!/bin/bash

### Shared Memory Size in Case of Pytorch Batch Training

# Get total memory in megabytes
TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_MEM_MB=$((TOTAL_MEM / 1024))
TOTAL_MEM_GB=$((TOTAL_MEM_MB / 1024))

# Calculate N% of total memory
SHM_SIZE_MB=$((TOTAL_MEM_MB * 50 / 100))

# Export as an environment variable
echo "Total Memory: $TOTAL_MEM_GB GB"
export SHM_SIZE=$TOTAL_MEM_GB

### run with source ./run_before_docker_compose.sh