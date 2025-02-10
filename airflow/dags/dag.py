from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta

default_args = {
    "start_date": datetime(2025, 1, 1),
    "schedule_interval": timedelta(minutes = 1),
    "catchup": False
}

### -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" 옵션 내용 확인 필요
### 컨테이너 default 네트워크 연결 필요 이유 확인

with DAG("crypto_trading", default_args = default_args) as dag:

    save_coinpedia_data = BashOperator(
        task_id = "save_coinpedia_data",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task s_coinpedia"'
    )

    save_coinpress_data = BashOperator(
        task_id = "save_coinpress_data",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task s_coinpress"'
    )

    save_price_data = BashOperator(
        task_id = "save_price_data",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task s_price"'
    )

    save_chart_data = BashOperator(
        task_id = "save_chart_data",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task s_chart"'
    )



    trade_crypto = BashOperator(
        task_id = "trade_crypto",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task trade"'
    )

    save_trade_log = BashOperator(
        task_id = "save_trade_log",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task s_log"'
    )

    evaluate_model = BashOperator(
        task_id = "evaluate_model",
        bash_command = 'ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" root@trader ' \
                        + '"cd /workspace && python dag_functions.py --task eval"'
    )



    [[save_coinpedia_data, save_coinpress_data, save_price_data, save_chart_data] >> trade_crypto]

    [trade_crypto >> save_trade_log >> evaluate_model]