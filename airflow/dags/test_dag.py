from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime

with DAG("test_once", start_date = datetime(2025, 1, 1), schedule_interval = "@once", catchup = False) as dag:
    test_once = BashOperator(
        task_id = "test_once",
        bash_command = 'echo Should Run Only Once'
    )

with DAG("test_dag", start_date = datetime(2025, 1, 1), schedule_interval = "@daily", catchup = False) as dag:
    test_task1 = BashOperator(
        task_id = "test_task1",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python ./airflow/airflow_test.py --test 1"'
    )

    test_task2 = BashOperator(
        task_id = "test_task2",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python ./airflow/airflow_test.py --test 2"'
    )

    ### Error
    test_task3 = BashOperator(
        task_id = "test_task3",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python ./airflow/airflow_test.py --test 1"'
    )

    test_task1 >> test_task2 >> test_task3