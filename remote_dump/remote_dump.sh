#!/bin/bash

DUMP_PATH=/remote_dump/crypto_db.sql
mysqldump -h $MYSQL_REMOTE_SOURCE -u $MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD crypto_db > $DUMP_PATH
mysql -u $MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD crypto_db < $DUMP_PATH
echo "At $(date), Refreshed Crypto DB" >> /remote_dump/scheduler.log

### cron setup
### */15 * * * * docker exec remote_mysql /remote_dump/remote_dump.sh