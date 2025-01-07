import json
import datetime
from dateutil.parser import parse

class DataCaller:
    def __init__(self, coin_name):
        self.coin_name = coin_name

    def get_data(self, days = 1):
        sentiment_data = self.read_news_sentiment_data(days)
        price_data = self.get_prices()
        price_data.update(sentiment_data)

        return price_data

    def read_news_sentiment_data(self, days):
        paths = [f"./Database/{self.coin_name}_coinpedia.json",
                 f"./Database/{self.coin_name}_coinpress.json"]
        
        sentiment_values = 0
        for path in paths:
            with open(path, "r", encoding = 'utf-8-sig') as f:
                data = json.load(f)
            sentiment_values += self.get_days_sentiment(data, days)
        
        return {f"{days}_days_sentiment_value": sentiment_values / len(paths)}
        
    def get_days_sentiment(self, data, days):
        current_date = datetime.datetime.now().date()
        days_before = current_date - datetime.timedelta(days = days)

        i = 0
        temp_data = {"Negative": 0, "Neutral": 0, "Positive": 0}
        while parse(data[i]['date']).date() >= days_before:
            if data[i]['sentiment'] == "Negative":
                temp_data["Negative"] += 1
            elif data[i]['sentiment'] == "Neutral":
                temp_data["Neutral"] += 1
            else:
                temp_data["Positive"] += 1
            i += 1
        
        ### 평균 값 구하는 로직 변경 가능
        ### 현재는 중립까지 고려한 positive의 강도 측정
        if i > 0:
            avg_value = (temp_data["Positive"] - temp_data["Negative"]) / i
        else:
            avg_value = 0

        return avg_value

    def get_prices(self):
        with open(f"./Database/{self.coin_name}_price_data.json", "r", encoding = 'utf-8-sig') as f:
            price_data = json.load(f)
        
        return price_data[0] ### 가장 최신 가격 데이터만 필요
