import os
import sys
from typing import List

import requests
import json
import datetime
from dateutil.parser import parse
from pytz import timezone

class UpbitPrice:
    def __init__(self, coin_name: str, crypto_info_path: str = "./Database/"):
        self.crypto_info_path = '%s%s' % (crypto_info_path, 'crypto_info.json')
        self.coin_name = coin_name
        self.token = self.__get_token()
        self.current_date = datetime.datetime.now(timezone('Asia/Seoul'))
    
    def __call__(self):
        self.__save_data()
    
    def __get_token(self) -> str:
        if not os.path.isfile(self.crypto_info_path):
            print(f"No Crypto Info Found; Building an Info File on {self.crypto_info_path}")
            self.__collect_crypto_info(self.crypto_info_path)
        
        with open(self.crypto_info_path, 'r', encoding = 'utf-8-sig') as f:
            crypto_info = json.load(f)
        
        ### 정렬된 리스트, 이진탐색으로 토큰 탐색
        self.token_index = self.__binary_search(crypto_info)
        if self.token_index < 0:
            sys.exit("Token Not Found")
        
        return crypto_info[self.token_index]['market']
    
    def __binary_search(self, crypto_info: List[dict]) -> int:
        start = 0
        end = len(crypto_info) - 1

        while start <= end:
            mid = (start + end) // 2

            if crypto_info[mid]['english_name'].lower() == self.coin_name.lower(): return mid
            elif crypto_info[mid]['english_name'].lower() > self.coin_name.lower(): end = mid - 1
            else: start = mid + 1
        
        return -1

    def __collect_crypto_info(self, crypto_info_path: str) -> None:
        url = "https://api.upbit.com/v1/market/all"
        resp = requests.get(url)

        ### BTC-ETH와 같이 비트코인이 화폐단위인 경우도 있음
        ### KRW로 시작하는 토큰만 추출
        crypto_info = []
        for crypto in resp.json():
            if crypto["market"].startswith("KRW"):
                crypto_info.append(crypto)
        
        ### 영문명으로 정렬
        crypto_info = sorted(crypto_info, key = lambda x: x['english_name'])

        with open(crypto_info_path, 'w', encoding = 'utf-8-sig') as f:
            json.dump(crypto_info, f, ensure_ascii = False)

    def __get_prices(self) -> dict:
        ### API로 한 번에 가격 정보 호출 가능
        payload = {"markets": self.token}
        url = "https://api.upbit.com/v1/ticker"
        resp = requests.get(url, params = payload)
        price_info = {
            "token": resp.json()[0]['market'],
            "trade_date_kst": str(parse(resp.json()[0]['trade_date_kst']).date()),
            "trade_time_kst": resp.json()[0]['trade_time_kst'],
            "opening_price": resp.json()[0]['opening_price'],
            "high_price": resp.json()[0]['high_price'],
            "low_price": resp.json()[0]['low_price'],
            "trade_price": resp.json()[0]['trade_price'],
            "signed_change_rate": resp.json()[0]['signed_change_rate'],
        }

        return price_info

    ### 주의, 유의 지정 여부
    def __get_market_events(self) -> dict:
        url = "https://api.upbit.com/v1/market/all"
        payload = {'is_details': True}
        resp = requests.get(url, params = payload)

        ### collect_crypto_info와 동일한 response, 
        ### 실시간으로 계속 호출을 수행하는데 매번 정렬하고 이진탐색을 수행하기보다는 단순히 선형으로 탐색하는 것이 효율적
        for crypto in resp.json():
            if crypto['market'] == self.token:
                break
        
        event_info = {
            "warning": crypto['market_event']['warning'],
            "price_fluctuations": crypto['market_event']['caution']['PRICE_FLUCTUATIONS'],
            "trading_volume_soaring": crypto['market_event']['caution']['TRADING_VOLUME_SOARING'],
            "deposit_amount_soaring": crypto['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
            "global_price_differences": crypto['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
            "concentration_of_small_accounts": crypto['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
        }

        return event_info
    
    def __save_data(self) -> None:
        data = self.__get_prices()
        data.update(self.__get_market_events())
        data = [data] ### dictionary로 구성된 리스트

        file_path = f"./Database/{self.coin_name}_price_data.json"
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)
        else:
            with open(file_path, "r", encoding = 'utf-8-sig') as f:
                cur_data = json.load(f)
            
            data += cur_data

            months_3_before = self.current_date - datetime.timedelta(days = 90)
            ### 끝에서부터 3개월 전 날짜에 해당하는 데이터들 삭제
            while(data[-1]['trade_date_kst'] == str(months_3_before.date())):
                data.pop()
            
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)
    
