#!/bin/bash

### For Running at Every 30 Minutes Passed
### */30 * * * * bash ABS_PATH/scheduled_task.sh

### For Running at Every 30 Minutes
### 30 * * * * bash ABS_PATH/scheduled_task.sh

### Clone Remote DB
docker exec remote_mysql /remote_dump/remote_dump.sh

### Calculate Metrics
docker exec metrics_calculator python /workspace/metrics_calculation.py