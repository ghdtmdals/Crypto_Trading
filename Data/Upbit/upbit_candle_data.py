import os
import requests
import matplotlib.pyplot as plt
import datetime
from dateutil.parser import parse
from pytz import timezone

from PIL import Image
import torch
from torchvision import transforms

class UpbitCandle:
    def __init__(self, token: str, days: int, price_type: str):
        self.token = token
        self.days = days
        self.price_type = price_type
        self.root = "./Database/chart_images/%s" % self.token
        self.url = "https://api.upbit.com/v1/candles/days"
        self.image_path = None

        ### 코인 별로 별도 폴더에 저장
        if not os.path.isdir(self.root):
            os.makedirs(self.root)

    def __call__(self) -> torch.Tensor:
        return self.get_image_tensor()

    def save_chart_image(self) -> None:
        self.delete_past_chart()

        params = {"market": self.token, "count": self.days}
        
        while True:
            try:
                resp = requests.get(self.url, params = params)
                break
            except Exception as e:
                print(e)

        price_data = []
        for data in resp.json():
            price_data.append(data[self.price_type]) ### 최신순으로 정렬되어있음

        ### convert to image
        now = datetime.datetime.now(timezone('Asia/Seoul')).date()
        self.image_path = '%s/%s.png' % (self.root, str(now))
        self.convert_to_image(price_data)

    def get_image_tensor(self) -> torch.Tensor:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            ### 채널 별 평균 및 표준편차 값 사용
            transforms.Normalize((0.9803, 0.9872, 0.9919), (0.1095, 0.0704, 0.0459))
        ])

        chart_image = Image.open(self.image_path).convert("RGB")

        return transform(chart_image)
    
    def convert_to_image(self, price_data) -> None:
        plt.gca().axes.xaxis.set_visible(False)
        plt.gca().axes.yaxis.set_visible(False)
        plt.plot(list(reversed(price_data)), linewidth = 2.5, color = 'dodgerblue')
        plt.savefig(self.image_path, dpi = 100, bbox_inches = 'tight', pad_inches = 0)
    
    def delete_past_chart(self) -> None:
        past_date = datetime.datetime.now(timezone('Asia/Seoul')).date() - datetime.timedelta(days = 90) ### 90일간 데이터만 유지
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
