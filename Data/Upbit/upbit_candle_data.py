import requests
from PIL import Image
import torch

class UpbitCandle:
    def __init__(self, token):
        self.token = token
        self.url = "https://api.upbit.com/v1/candles/days"

    def __call__(self, days: int = 90, price_type: str = 'high_price'):
        ### 조회 가능하도록
        self.days = days
        self.price_type = price_type
        self.get_candle_data()

    def get_candle_data(self):
        ### get data
        params = {"market": self.token, "cound": self.days}
        resp = requests.get(self.url, params = params)
        price_data = []
        for data in resp.json():
            price_data.append(data[self.price_type]) ### 최신순으로 정렬되어있음

        ### convert to image

        ### convert to tensor
        pass

    def convert_to_image(self):
        pass