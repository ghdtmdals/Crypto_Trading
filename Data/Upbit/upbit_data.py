import keys
import requests
from typing import List

class UpbitPrice:
    def __init__(self):
        pass
    
    def get_prices(self) -> List[float]:
        ### API로 한 번에 호출 가능
        pass

    ### 주의, 유의 지정 여부 구현
    def get_market_events(self) -> bool:
        pass
    
    def merge_data(self) -> list:
        ### 데이터 통합
        pass

    def save_data(self) -> None:
        ### 데이터 저장
        pass
