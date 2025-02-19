#!/bin/bash

nowdate=$(date)
echo "It is ${nowdate}, crontab test success." >> $PWD/cron.log

# */1 * * * * bash /mnt/d/Python_Source/Crypto_Trading/power_bi/crontab_test.sh
# */15 * * * * docker exec remote_db /remote_dump/remote_dump.sh
# */15 * * * * docker exec metrics_calculator python /workspace/metrcis_calculation.py