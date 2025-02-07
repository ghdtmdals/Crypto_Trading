from typing import List
import requests
import datetime
from dateutil.parser import parse
from pytz import timezone

class UpbitPrice:
    def __init__(self, token: str):
        self.token = token
        self.current_date = datetime.datetime.now(timezone('Asia/Seoul'))
    
    def __call__(self) -> tuple:
        # self.__save_data()
        data = self.get_prices()
        data.update(self.get_market_events())

        return (data['token'], data['trade_date_kst'], data['trade_time_kst'], data['high_price'], data['low_price'],
                data['opening_price'], data['trade_price'], data['signed_change_rate'], data['warning'],
                data['deposit_amount_soaring'], data['global_price_differences'], data['price_fluctuations'],
                data['trading_volume_soaring'], data['concentration_of_small_accounts'])

    def get_prices(self) -> dict:
        ### API로 한 번에 가격 정보 호출 가능
        payload = {"markets": self.token}
        url = "https://api.upbit.com/v1/ticker"
        
        while True:
            try:
                resp = requests.get(url, params = payload)
                break
            except Exception as e:
                print(e)

        price_info = {
            "token": resp.json()[0]['market'],
            "trade_date_kst": str(parse(resp.json()[0]['trade_date_kst']).date()),
            "trade_time_kst": resp.json()[0]['trade_time_kst'],
            "high_price": resp.json()[0]['high_price'],
            "low_price": resp.json()[0]['low_price'],
            "opening_price": resp.json()[0]['opening_price'],
            "trade_price": resp.json()[0]['trade_price'],
            "signed_change_rate": resp.json()[0]['signed_change_rate'],
        }

        return price_info

    ### 주의, 유의 지정 여부
    def get_market_events(self) -> dict:
        url = "https://api.upbit.com/v1/market/all"
        payload = {'is_details': True}

        while True:
            try:
                resp = requests.get(url, params = payload)
                break
            except Exception as e:
                print(e)

        ### collect_crypto_info와 동일한 response, 
        ### 실시간으로 계속 호출을 수행하는데 매번 정렬하고 이진탐색을 수행하기보다는 단순히 선형으로 탐색하는 것이 효율적
        for crypto in resp.json():
            if crypto['market'] == self.token:
                break
        
        event_info = {
            "warning": crypto['market_event']['warning'],
            "deposit_amount_soaring": crypto['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
            "global_price_differences": crypto['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
            "price_fluctuations": crypto['market_event']['caution']['PRICE_FLUCTUATIONS'],
            "trading_volume_soaring": crypto['market_event']['caution']['TRADING_VOLUME_SOARING'],
            "concentration_of_small_accounts": crypto['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
        }

        return event_info
    
    # def __save_data(self) -> None:
    #     data = self.__get_prices()
    #     data.update(self.__get_market_events())
    #     data = [data] ### dictionary로 구성된 리스트

    #     file_path = f"./Database/{self.coin_name}_price_data.json"
    #     if not os.path.isfile(file_path):
    #         with open(file_path, "w", encoding = 'utf-8-sig') as f:
    #             json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)
    #     else:
    #         with open(file_path, "r", encoding = 'utf-8-sig') as f:
    #             cur_data = json.load(f)
            
    #         data += cur_data

    #         months_3_before = self.current_date - datetime.timedelta(days = 90)
    #         ### 끝에서부터 3개월 전 날짜에 해당하는 데이터들 삭제
    #         while(data[-1]['trade_date_kst'] == str(months_3_before.date())):
    #             data.pop()
            
    #         with open(file_path, "w", encoding = 'utf-8-sig') as f:
    #             json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)
    
