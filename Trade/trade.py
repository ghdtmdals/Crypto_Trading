import os

import jwt
import uuid
import hashlib
import requests
from urllib.parse import urlencode, unquote

import time
import datetime
from pytz import timezone
import json

from Data.data.save_data import DataCrawler
from Model.Network.trade_algorithm import TradeStrategy
from Trade.data_caller import DataCaller

class Trader:
    def __init__(self, coin_name: str):
        self.__access_key = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.__secret_key = os.environ["UPBIT_OPEN_API_SECRET_KEY"]

        self.coin_name = coin_name
        self.token = None

    ### 토큰의 밸런스를 가져오기 위해 토큰이 몇 번째 인덱스인지 찾음
    ### token = "KRW-BTC" -> currency = "BTC"
    def find_token(self, balance_info: list, currency: str) -> int:
        for i in range(len(balance_info)):
            if balance_info[i]['currency'] == currency:
                return i
        return -1
    
        ### 새로운 코인이 추가되었는지 저장된 리스트와 비교 후 추가
    def check_new_crypto(self) -> None:
        url = "https://api.upbit.com/v1/market/all"
        resp = requests.get(url)

        new_crypto_info = []
        for crypto in resp.json():
            if crypto["market"].startswith("KRW"):
                new_crypto_info.append(crypto)
        
        ### 영문명으로 정렬
        new_crypto_info = sorted(new_crypto_info, key = lambda x: x['english_name'])

        with open(self.crypto_info_path, 'r', encoding = 'utf-8-sig') as f:
            cur_crypto_info = json.load(f)
        
        ### 새로운 코인이 추가되었거나, 기존 코인이 사라지는 등 차이가 발생한 경우 새로운 코인 리스트 저장
        ### 트레이딩 과정에서 일정 주기 (EX. 1일)로 호출해야 함
        if new_crypto_info != cur_crypto_info:
            with open(self.crypto_info_path, 'w', encoding = 'utf-8-sig') as f:
                json.dump(new_crypto_info, f, ensure_ascii = False)
            print("\nNew Crypto List Info Saved")
        else:
            print("\nNo Change in Crypto List Info")

    def get_current_balance(self) -> dict:
        url = "https://api.upbit.com/v1/accounts"

        payload = {
            'access_key': self.__access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.__secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
        'Authorization': authorization,
        }

        resp = requests.get(url, headers=headers)
        balance_info = resp.json()

        krw_index = self.find_token(balance_info, "KRW")
        token_index = self.find_token(balance_info, self.token.split("-")[1]) ### KRW-BTC -> [KRW, -, BTC] -> BTC

        if token_index == -1: ### 아직 구매한 코인이 없으면 -1
            balance = {"krw_balance": float(balance_info[krw_index]['balance']),
                       "token_balance": 0}
        else:
            balance = {"krw_balance": float(balance_info[krw_index]['balance']),
                       "token_balance": float(balance_info[token_index]['balance'])}
        
        return balance
    
    def trade(self, call: str, proportion: int, balance: dict) -> dict:
        if call == "hold":
            return {"trade_result": "no trade"}
        
        if call == "bid":
            params = self.bid(balance, proportion)

        elif call == "ask":
            params = self.ask(balance, proportion)

        url = "https://api.upbit.com/v1/orders"
        
        ### jwt 토큰 생성 과정
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.__access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.__secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        resp = requests.post(url, json=params, headers=headers)
        return resp.json()
    
    def bid(self, balance: dict, proportion: float) -> dict:
        params = {
            'market': self.token,
            'side': 'bid',
            'ord_type': 'price',
            'price': f"{int(balance['krw_balance'] * proportion * 0.95)}",
        }

        return params

    def ask(self, balance: dict, proportion: float) -> dict:
        params = {
            'market': self.token,
            'side': 'ask',
            'ord_type': 'market',
            'volume': f"{balance['token_balance'] * proportion}",
        }

        return params

    ### 데이터 모두 합쳐서 저장
    def save_log_data(self, save_path: str = "./Database/", *data) -> None:
        log = {'date': str(data[0].date()), 'time': str(data[0].time()),
               'krw_balance': data[1]['krw_balance'], 'token_balance': data[1]['token_balance'], 
               'trade_call': data[2], 'result': data[3]}

        file_path = '%s/%s' % (save_path, 'trade_log.json')
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump([log], f, ensure_ascii = False, indent = 4, sort_keys = True)

        else:
            with open(file_path, "r", encoding = 'utf-8-sig') as f:
                logs = json.load(f)

            logs.insert(0, log)
            if len(logs) > 10000: ### 1만개 로그만 저장
                logs = logs[:10000]
            
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(logs, f, ensure_ascii = False, indent = 4, sort_keys = True)

    def start_trading(self) -> None: 
        ### 데이터 모듈 초기화
        print("Loading Modules...")
        data_crawler = DataCrawler(coin_name = self.coin_name)
        data_caller = DataCaller(coin_name = self.coin_name)
        self.token = data_crawler.token
        
        ### 트레이딩 모듈 초기화
        trader = TradeStrategy(algorithm = "test")

        start_time = datetime.datetime.now(timezone('Asia/Seoul'))
        tomorrow = start_time.date() + datetime.timedelta(days = 1)

        
        print(f"Start Trading | Current Time {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        ### 시작할때 뉴스 데이터 한 번 수집
        data_crawler.get_news_data()
        while True:
            current_time = datetime.datetime.now(timezone('Asia/Seoul'))
            ### Data 수집
            ### 가격 데이터는 매 회 수집
            data_crawler.get_price_data()
            
            ### 데이터 호출
            data = data_caller.get_data(days = 1)

            ### balance 호출
            balance = self.get_current_balance()

            ### 트레이딩 전략 실행
            trade_call, proportion = trader(data, balance)
            data["call"] = trade_call
            data["proportion"] = proportion

            ### 주문 호출
            result = self.trade(trade_call, proportion, balance)

            ### 로그 데이터 저장
            self.save_log_data("./Database", current_time, balance, trade_call, result)

            ### 일정 시점마다 새로운 token 추가 여부 확인 (하루) + 뉴스 데이터 수집
            if current_time.date() == tomorrow and current_time.hour == 9:
                tomorrow = current_time.date() + datetime.timedelta(days = 1)
                self.check_new_crypto()
                data_crawler.get_news_data()

            print(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | " \
                  + f"Current KRW Balance: {balance['krw_balance']} | " \
                  + f"Currency {self.token} Balance: {balance['token_balance']} | Trade Call: {trade_call}")

            time.sleep(60)