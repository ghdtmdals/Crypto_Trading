import os
import sys
from typing import List

import requests
import json

class UpbitPrice:
    def __init__(self, data_path = "./Database/", coin_name: str = 'Bitcoin'):
        self.crypto_info_path = '%s%s' % (data_path, 'crypto_info.json')
        self.coin_name = coin_name
        self.token = self.get_token()
    
    def get_token(self) -> str:
        if not os.path.isfile(self.crypto_info_path):
            print(f"No Crypto Info Found; Building an Info File on {self.crypto_info_path}")
            self.collect_crypto_info(self.crypto_info_path)
        
        with open(self.crypto_info_path, 'r', encoding = 'utf-8-sig') as f:
            crypto_info = json.load(f)
        
        ### 정렬된 리스트이고 코인 수 자체가 그렇게 많지 않으니 이진탐색으로 토큰 탐색
        self.token_index = self.binary_search(crypto_info)
        if self.token_index < 0:
            sys.exit("Token Not Found")
        
        return crypto_info[self.token_index]['market']
    
    def binary_search(self, crypto_info: List[dict]) -> int:
        start = 0
        end = len(crypto_info) - 1

        while start <= end:
            mid = (start + end) // 2

            if crypto_info[mid]['english_name'].lower() == self.coin_name.lower(): return mid
            elif crypto_info[mid]['english_name'].lower() > self.coin_name.lower(): end = mid - 1
            else: start = mid + 1
        
        return -1

    def collect_crypto_info(self, crypto_info_path: str) -> None:
        url = "https://api.upbit.com/v1/market/all"
        resp = requests.get(url)

        crypto_info = []
        for crypto in resp.json():
            if crypto["market"].startswith("KRW"):
                crypto_info.append(crypto)
        
        ### 영문명으로 정렬
        crypto_info = sorted(crypto_info, key = lambda x: x['english_name'])

        with open(crypto_info_path, 'w', encoding = 'utf-8-sig') as f:
            json.dump(crypto_info, f, ensure_ascii = False)

    def get_prices(self) -> list:
        ### API로 한 번에 호출 가능
        payload = {"markets": self.token}
        url = "https://api.upbit.com/v1/ticker"
        resp = requests.get(url, params = payload)
        price_info = {
            "token": resp.json()[0]['market'],
            "trade_date_kst": resp.json()[0]['trade_date_kst'],
            "trade_time_kst": resp.json()[0]['trade_time_kst'],
            "opening_price": resp.json()[0]['opening_price'],
            "high_price": resp.json()[0]['high_price'],
            "low_price": resp.json()[0]['low_price'],
            "trade_price": resp.json()[0]['trade_price'],
        }

        return price_info

    ### 주의, 유의 지정 여부 구현
    def get_market_events(self) -> bool:
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
    
    ### 새로운 코인이 추가되었는지 저장된 리스트와 비교 후 추가
    def check_new_crypto(self):
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
            print("New Crypto List Info Saved")
        else:
            print("No Change in Crypto List Info")
