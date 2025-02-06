import argparse

from Data.News.coinpedia import CoinPedia
from Data.News.coinpress import CoinPress
from Data.Upbit.upbit_data import UpbitPrice
from Data.Upbit.upbit_candle_data import UpbitCandle

from Database.database import CryptoDB
from Model.Network.trade_strategy import TradeStrategy
from Trade.trade import Trader

def collect_coinpedia_data(): ...

def run_coinpedia_sentiment(): ...

def save_coinpedia_data(): ...

def collect_coinpress_data(): ...

def run_coinpress_sentiment(): ...

def save_coinpress_data(): ...

def collect_price_data(): ...

def save_price_data(): ...

def collect_chart_data(): ...

def save_chart_data(): ...

def load_news_data(): ...

def load_price_data(): ...

def load_chart_data(): ...

### 데이터 로딩 후 합쳐서 전달해야 함
def load_data():
    news_data = load_news_data()
    price_data = load_price_data()
    chart_data = load_chart_data()

def trade_crypto(): ...

def save_trade_log(): ...

def evaluate_model(): ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type = str)
    args = parser.parse_args()

    tasks = {'c_coinpedia': collect_coinpedia_data, 'sent_coinpedia': run_coinpedia_sentiment, 's_coinpedia': save_coinpedia_data, 
             'c_coinpress': collect_coinpress_data, 'sent_coinpress': run_coinpress_sentiment, 's_coinpress': save_coinpress_data,
             'c_price': collect_price_data, 's_price': save_price_data, 
             'c_chart': collect_chart_data, 's_chart': save_chart_data,
             'l_data': load_data, 'trade': trade_crypto, 's_log': save_trade_log, 'eval': evaluate_model}
    
    tasks[args.task]()