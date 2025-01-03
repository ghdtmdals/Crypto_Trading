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

from Data.Upbit.upbit_data import UpbitPrice
from Model.Network.trade_algorithm import TradeStrategy

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
            'price': f'{int(balance['krw_balance'] * proportion * 0.95)}',
        }

        return params

    def ask(self, balance: dict, proportion: float) -> dict:
        params = {
            'market': self.token,
            'side': 'ask',
            'ord_type': 'market',
            'volume': f'{balance['token_balance'] * proportion}',
        }

        return params

    ### 데이터 모두 합쳐서 저장
    def save_data(self, data: dict, save_path: str = "./Database/") -> None:
        file_path = '%s/%s' % (save_path, 'trade_log.json')
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump([data], f, ensure_ascii = False, indent = 4, sort_keys = True)

        else:
            with open(file_path, "r", encoding = 'utf-8-sig') as f:
                logs = json.load(f)

            logs.insert(0, data)
            if len(logs) > 10000: ### 1만개 로그만 저장
                logs = logs[:10000]
            
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(logs, f, ensure_ascii = False, indent = 4, sort_keys = True)

    def start_trading(self) -> None: 
        ### 데이터 모듈 초기화
        print("Loading Modules...")
        ### self.token = "Bitcoin"
        upbit_caller = UpbitPrice(coin_name = self.coin_name)
        ### self.token = "KRW-BTC"
        self.token = upbit_caller.token
        
        ### 트레이딩 모듈 초기화
        trader = TradeStrategy(algorithm = "test")

        start_time = datetime.datetime.now(timezone('Asia/Seoul'))
        tomorrow = start_time.date() + datetime.timedelta(days = 1)

        print(f"Start Trading | Current Time {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        while True:
            ### balance 호출
            balance = self.get_current_balance()

            ### 현재가 호출
            upbit_data = upbit_caller.get_prices()

            ### 유의종목 여부 호출, 딕셔너리에 바로 합침
            upbit_data.update(upbit_caller.get_market_events())

            ### 데이터 병합
            current_time = datetime.datetime.now(timezone('Asia/Seoul'))
            data = {"Time": current_time.strftime('%Y-%m-%d %H:%M:%S')}
            data.update(balance)
            data.update(upbit_data)

            ### 트레이딩 전략 실행
            trade_call, proportion = trader(data)
            data["call"] = trade_call
            data["proportion"] = proportion

            ### 주문 호출
            result = self.trade(trade_call, proportion, balance)
            data.update(result)

            ### 사용한 데이터 저장
            self.save_data(data)

            ### 일정 시점마다 새로운 token 추가 여부 확인
            if current_time.date() == tomorrow and current_time.hour == 9:
                tomorrow = current_time.date() + datetime.timedelta(days = 1)
                upbit_caller.check_new_crypto()

            print(f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | " \
                  + f"Current KRW Balance: {data['krw_balance']} | " \
                  + f"Currence {self.token} Balance: {data['token_balance']} | Trade Call: {trade_call}")

            time.sleep(60)