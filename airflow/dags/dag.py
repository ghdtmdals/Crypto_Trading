from airflow import DAG
from airflow.operators.python import PythonOperator

import requests
from datetime import datetime, timedelta
import pendulum

default_args = {
    "start_date": datetime(2025, 1, 1, tzinfo = pendulum.timezone("Asia/Seoul")),
}

### -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" 옵션 내용 확인 필요
### 컨테이너 default 네트워크 연결 필요 이유 확인

def _save_news_data():
    resp = requests.get("http://trader:4000/save-news")
    # print(resp.json())
    return resp.json()

def _save_price_data():
    resp = requests.get("http://trader:4000/save-price")
    return resp.json()

def _save_chart_data():
    resp = requests.get("http://trader:4000/save-chart")
    return resp.json()

def _trade_crypto():
    resp = requests.get("http://trader:4000/trade")
    return resp.json()

def _evaluate_mode():
    resp = requests.get("http://trader:4000/eval-model")
    return resp.json()

with DAG("crypto_trading", default_args = default_args, schedule_interval = timedelta(minutes = 1), catchup = False) as dag:

    save_news_data = PythonOperator(
        task_id = "save_news_data",
        python_callable = _save_news_data
    )

    save_price_data = PythonOperator(
        task_id = "save_price_data",
        python_callable = _save_price_data
    )

    save_chart_data = PythonOperator(
        task_id = "save_chart_data",
        python_callable = _save_chart_data
    )

    trade_crypto = PythonOperator(
        task_id = "trade_crypto",
        python_callable = _trade_crypto
    )

    evaluate_model = PythonOperator(
        task_id = "evaluate_model",
        python_callable = _evaluate_mode
    )
    

    [[save_news_data, save_price_data, save_chart_data] >> trade_crypto >> evaluate_model]