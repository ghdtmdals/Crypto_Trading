import os
import requests
import matplotlib.pyplot as plt
import datetime
from dateutil.parser import parse

from PIL import Image
import torch
from torchvision import transforms

class UpbitCandle:
    def __init__(self, token):
        self.token = token
        self.root = "./Database/chart_images/%s" % self.token
        self.url = "https://api.upbit.com/v1/candles/days"

        ### 코인 별로 별도 폴더에 저장
        if not os.path.isdir(self.root):
            os.mkdir(self.root)

    def __call__(self, days: int = 90, price_type: str = 'high_price') -> torch.Tensor:
        self.days = days
        self.price_type = price_type
        self.delete_past_chart()
        return self.get_candle_data()

    def get_candle_data(self) -> torch.Tensor:
        ### get data
        params = {"market": self.token, "count": self.days}
        resp = requests.get(self.url, params = params)
        price_data = []
        for data in resp.json():
            price_data.append(data[self.price_type]) ### 최신순으로 정렬되어있음

        ### convert to image
        now = datetime.datetime.now().date()
        image_path = '%s/%s.png' % (self.root, str(now))
        self.convert_to_image(price_data, image_path)

        ### convert to tensor
        return self.get_image_tensor(image_path)
        

    def convert_to_image(self, price_data, image_path) -> None:
        plt.gca().axes.xaxis.set_visible(False)
        plt.gca().axes.yaxis.set_visible(False)
        plt.plot(list(reversed(price_data)), linewidth = 2.5, color = 'dodgerblue')
        plt.savefig(image_path, dpi = 100, bbox_inches = 'tight', pad_inches = 0)
    
    def get_image_tensor(self, image_path) -> torch.Tensor:
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            ### 채널 별 평균 및 표준편차 값 사용
            transforms.Normalize((0.9803, 0.9872, 0.9919), (0.1095, 0.0704, 0.0459))
        ])

        chart_image = Image.open(image_path).convert("RGB")

        return transform(chart_image)
    
    def delete_past_chart(self):
        past_date = datetime.datetime.now().date() - datetime.timedelta(days = self.days)
        chart_images = os.listdir(self.root)

        for image in chart_images:
            file_name = os.path.splitext(image)[0]
            if parse(file_name).date() < past_date:
                file = '%s/%s.png' % (self.root, file_name)
                os.remove(file)
            
            ### 앞에 있는 데이터가 가장 오래된 데이터 순서로 정렬되어있음
            ### 오래된 데이터가 self.days 이전보다 오래되지 않았으면 종료
            else:
                break
