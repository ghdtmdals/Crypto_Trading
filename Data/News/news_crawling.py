import os

import requests
from bs4 import BeautifulSoup
import json

import datetime
from dateutil.parser import parse

from Data.News.sentiment_analysis import Sentiment

class NewsCrawling:
    def __init__(self):
        self.coin_name = None
        self.token = None

        self.source = None
        self.params = None
        self.url = None
        
        self.current_date = None

    def get_news_data(self, title_block_tag: str, title_block_class_name: str, title_tag: str, \
                  title_class_name: str, date_tag: str, date_class_name: str) -> list:
        sentiment_analyzer = Sentiment()

        ### 오늘자 뉴스만 가져옴
        while True:
            try:
                resp = requests.get(self.url, params = self.params)
                break
            except Exception as e:
                print(e)

        soup = BeautifulSoup(resp.text, 'html.parser')
        coinpedia_news = soup.find_all(title_block_tag, title_block_class_name)

        news_data = []
        for news in coinpedia_news:
            temp_data = {}
            title = self.get_title(news, title_tag, title_class_name)
            date = self.get_date(news, date_tag, date_class_name)
            
            ### 수집 되는거 그냥 다 수집
            temp_data = (self.token, str(date.date()), self.source, title, self.run_sentiment(sentiment_analyzer, title))
            news_data.append(temp_data)
            # if date.date() == self.current_date.date():
            #     temp_data = (self.token, str(date.date()), self.source, title, self.__run_sentiment(sentiment_analyzer, title))
            #     news_data.append(temp_data)
            # else: ### 최신순으로 출력됨
            #     break
        
        return news_data

    def get_title(self, soup, title_tag: str, title_class_name: str) -> str:
        ### 뉴스 타이틀만 호출
        title = soup.find(title_tag, title_class_name).text
        return title

    def get_date(self, soup, date_tag: str, date_class_name: str) -> datetime.datetime:
        ### 날짜 가져오기
        date = soup.find(date_tag, date_class_name).text
        ### 'B d(0패딩 x), YYYY' -> 'YYYY-MM-DD'
        ### Ex) 'January 3, 2025' -> '2025-01-03'
        date = parse(date)
        return date
    
    def run_sentiment(self, analyzer, text: str) -> str:
        result = analyzer.get_sentiment(text)
        ### 0, 1, 2로 출력됨
        ### 나중에 보면 헷갈릴 수 있으니 단어로 변환해 저장
        if result == 0:
            return "Negative"
        elif result == 1:
            return "Neutral"
        else:
            return "Positive"