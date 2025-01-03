import os
import requests
from bs4 import BeautifulSoup
import json
from typing import List
import datetime
from dateutil.parser import parse
from pytz import timezone

class CoinPress:
    def __init__(self, coin_name: str):
        ### 영어 + 한국어 뉴스 수집
        self.coin_name = coin_name
        self.params = {"s": self.coin_name} ### Ex) Bitcoin
        self.url = "https://coinspress.com/"
        self.current_date = None
    
    def __call__(self) -> None:
        self.current_date = datetime.datetime.now(timezone('Asia/Seoul'))
        self.save_data()

    def get_news_data(self) -> list:
        ### 오늘자 뉴스만 가져와야됨
        resp = requests.get(self.url, params = self.params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        coinpedia_news = soup.find_all('div', "col-12 order-3 order-md-2 col-md-4")

        news_data = []
        for news in coinpedia_news:
            temp_data = {}
            title = self.get_title(news)
            date = self.get_date(news)
            if date.date() == self.current_date.date():
                temp_data['date'] = str(date.date())
                temp_data['title'] = title
                news_data.append(temp_data)
            else: ### 최신순으로 출력됨
                break
        
        return news_data

    def get_title(self, soup) -> str:
        ### 뉴스 타이틀만 호출
        title = soup.find('h2', "post-title").text
        return title

    def get_date(self, soup) -> datetime.datetime:
        ### 날짜 가져오기
        date = soup.find('li', "list-inline-item post-date").text
        ### 'B d(0패딩 x), YYYY' -> 'YYYY-MM-DD'
        ### Ex) 'January 3, 2025' -> '2025-01-03'
        date = parse(date)
        return date

    def save_data(self) -> None:
        data = self.get_news_data()
        file_path = f"./Database/{self.coin_name}_coinpress.json"
        if not os.path.isfile(file_path):
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)
        else:
            with open(file_path, "r", encoding = 'utf-8-sig') as f:
                cur_data = json.load(f)
            
            data += cur_data

            months_3_before = self.current_date - datetime.timedelta(days = 90)
            ### 끝에서부터 3개월 전 날짜에 해당하는 데이터들 삭제
            while(data[-1]['date'] == str(months_3_before.date())):
                data.pop()
            
            with open(file_path, "w", encoding = 'utf-8-sig') as f:
                json.dump(data, f, ensure_ascii = False, indent = 4, sort_keys = True)

if __name__ == "__main__":
    coinpress = CoinPress('Bitcoin')
    # data = coinpress.get_news_data()
    coinpress()
    print("Done")