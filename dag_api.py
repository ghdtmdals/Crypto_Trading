# from fastapi import FastAPI
from flask import Flask
import datetime
from pytz import timezone

from Database.database import CryptoDB
from Model.Network.trade_strategy import TradeStrategy
from Trade.trade import Trader

##################################### Initializing Instance #####################################
app = Flask(__name__)

app.coin_name = "Bitcoin"
app.crypto_db = CryptoDB(coin_name = app.coin_name)
app.token = app.crypto_db.token

app.trade_strategy = TradeStrategy(app.token, "basic", learning_rate = 1e-5)
app.trader = Trader(coin_name = app.coin_name, token = app.token)
#################################################################################################

@app.route("/test", methods = ['GET'])
def print_coin_name():
    return {"coin_name": app.coin_name}

@app.route("/save-news", methods = ['GET'])
def save_news_data():
    app.crypto_db.save_news_data()
    return {"result": "News Data Saved"}

@app.route("/save-price", methods = ['GET'])
def save_price_data():
    app.crypto_db.save_price_data()
    return {"result": "Price Data Saved"}

@app.route("/save-chart", methods = ['GET'])
def save_chart_data():
    app.crypto_db.save_chart_data()
    return {"result": "Chart Image Saved"}

@app.route("/trade", methods = ['GET'])
def trade_crypto():
    data, image_data = app.crypto_db.load_data(sentiment_days = 1, sentiment_type = 'all', sentiment_alpha = 0.5)

    balance = app.trader.get_current_balance()

    change_rate, avg_change_rate = app.crypto_db.get_target()
    target = app.trade_strategy.get_target(change_rate, avg_change_rate)
    trade_call = app.trade_strategy(data, image_data, target)

    if app.trade_strategy.get_accuracy(app.crypto_db.get_eval_data()) >= 0.5:
        result = app.trader.trade(trade_call, balance)
    else:
        result = {"no trade": "accuracy not sufficient"}

    current_time = datetime.datetime.now(timezone('Asia/Seoul'))
    app.crypto_db.save_log_data(current_time, balance, trade_call, app.trade_strategy.calls[target], result)
    
    return {"trade_call": trade_call, "result": result}

@app.route("/eval-model", methods = ['GET'])
def evaluate_model():
    scores = app.trade_strategy.eval(app.crypto_db.get_eval_data())
    return {"scores": scores}

### 실행 (Flask)
if __name__ == "__main__":
    app.run(debug = False, host = '0.0.0.0', port = 4000)


### 실행 (FastAPI)
# uvicorn dag_api:app --reload --host=0.0.0.0 --port=4000