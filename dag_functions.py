import argparse

import os
import pymysql

from Data.News.coinpedia import CoinPedia
from Data.News.coinpress import CoinPress
from Data.Upbit.upbit_data import UpbitPrice
from Data.Upbit.upbit_candle_data import UpbitCandle

from Database.database import CryptoDB
from Model.Network.trade_strategy import TradeStrategy
from Trade.trade import Trader

def collect_coinpedia_data() -> None: ...

def save_coinpedia_data() -> None: ...

def collect_coinpress_data() -> None: ...

def save_coinpress_data() -> None: ...

def collect_price_data() -> None: ...

def save_price_data() -> None: ...

def collect_chart_data() -> None: ...

def save_chart_data() -> None: ...

def load_news_data(): ...

def load_price_data(): ...

def load_chart_data(): ...

### 데이터 로딩 후 합쳐서 전달해야 함
def load_data():
    news_data = load_news_data()
    price_data = load_price_data()
    chart_data = load_chart_data()

def trade_crypto():
    load_data()

def save_trade_log(): ...

def evaluate_model(): ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type = str)
    args = parser.parse_args()

    tasks = {'s_coinpedia': save_coinpedia_data, 's_coinpress': save_coinpress_data,
             's_price': save_price_data, 's_chart': save_chart_data,
             'trade': trade_crypto, 's_log': save_trade_log, 'eval': evaluate_model}
    
    tasks[args.task]()
