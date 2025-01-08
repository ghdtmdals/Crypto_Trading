import os
import mysql.connector
import json

import requests
from Data.Upbit.upbit_data import UpbitPrice
from Data.News.coinpedia import CoinPedia
from Data.News.coinpress import CoinPress

class CryptoDB:
    def __init__(self, coin_name):
        self.conn = mysql.connector.connect(
                        host = 'mysqldb',
                        user = os.environ['MYSQL_USER'],
                        password = os.environ['MYSQL_PASSWORD'],
                        database = os.environ['MYSQL_DATABASE']
                    )
        self.cursor = self.conn.cursor(dictionary = True)
        self.create_tables()
        self.collect_crypto_info()

        self.coin_name = coin_name
        self.token = self.get_token()

        self.upbit = UpbitPrice(token = self.token)
        self.news = [CoinPedia(self.coin_name, self.token), CoinPress(self.coin_name, self.token)]
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()

    ### DB 테이블 생성
    def create_tables(self):
        with open("./Database/create_tables.sql", "r") as f:
            sql = f.read()
        self.cursor.execute(sql)
        self.conn.reconnect()
    
    def get_token(self):
        query = f"SELECT token FROM Crypto_Info WHERE english_name = '{self.coin_name}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0]['token'] ### [(token, )]

    ### 일정 주기로 호출되도록 설정
    def collect_crypto_info(self):
        print("Checking for Newly Listed Crypto Information")
        url = "https://api.upbit.com/v1/market/all"
        resp = requests.get(url)

        ### BTC-ETH와 같이 비트코인이 화폐단위인 경우도 있음
        ### KRW로 시작하는 토큰만 추출
        crypto_info = []
        for crypto in resp.json():
            if crypto["market"].startswith("KRW"):
                crypto_info.append((crypto['market'], crypto['english_name'], crypto['korean_name']))
        
        query = "INSERT IGNORE INTO Crypto_Info (token, english_name, korean_name) VALUES (%s, %s, %s);"
        self.cursor.executemany(query, crypto_info)
        self.conn.commit()

    def save_price_data(self):
        data = self.upbit()
        query = "INSERT INTO Upbit (" \
                + "token, trade_date_kst, trade_time_kst, high_price, low_price, opening_price, trade_price, signed_change_rate, " \
                + "warning, deposit_amount_soaring, global_price_differences, price_fluctuations, " \
                + "trading_volume_soaring, concentration_of_small_accounts" \
                + ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, data)
        self.conn.commit()

    def save_news_data(self):
        for news in self.news:
            print(f"Collecting {news.coin_name} News Data From {news.source}")
            data = news()
            query = "INSERT IGNORE INTO News (token, news_date, news_source, title, sentiment) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.executemany(query, data)
            self.conn.commit()
    
    def save_log_data(self, *data):
        log = (self.token, str(data[0].date()), str(data[0].time()), 
               data[1]['krw_balance'], data[1]['token_balance'], data[2], json.dumps(data[3]))

        query = "INSERT INTO Trade_Log (" \
                + "token, trade_date, trade_time, krw_balance, token_balance, trade_call, trade_result" \
                + ") VALUES(%s, %s, %s, %s, %s, %s, %s)"
        
        self.cursor.execute(query, log)
        self.conn.commit()

    def load_data(self, sentiment_days = 1):
        query = "CREATE TEMPORARY TABLE Temp_Sentiment (" \
                + "SELECT token, AVG(sentiment) AS sentiment " \
                + "FROM " \
                + "(SELECT token, news_date, " \
                + "CASE " \
                + "WHEN sentiment = 'Negative' THEN 0 " \
                + "WHEN sentiment = 'Neutral' THEN 1 " \
                + "WHEN sentiment = 'Positive' THEN 2 " \
                + "END AS Sentiment " \
                + "FROM `News`) N " \
                + f"WHERE news_date >= DATE_SUB(DATE(NOW()), INTERVAL {sentiment_days} DAY) " \
                + "GROUP BY token);"
        
        self.cursor.execute(query)
        query = "SELECT * FROM Temp_Sentiment S LEFT JOIN Upbit U ON S.token = U.token " \
                + "WHERE U.trade_date_kst = DATE(NOW()) ORDER BY U.trade_date_kst DESC, U.trade_time_kst DESC LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()[0]

        ### 사용 후 삭제해야 중복 생성 에러 발생하지 않음
        query = "DROP TEMPORARY TABLE Temp_Sentiment;"
        self.cursor.execute(query)

        ### MySQL 데이터 타입 -> Python 데이터 타입
        result['sentiment'] = float(result['sentiment'])
        result['trade_date_kst'] = str(result['trade_date_kst'])
        result['trade_time_kst'] = str(result['trade_time_kst'])
        result['high_price'] = float(result['high_price'])
        result['low_price'] = float(result['low_price'])
        result['opening_price'] = float(result['opening_price'])
        result['trade_price'] = float(result['trade_price'])
        result['signed_change_rate'] = float(result['signed_change_rate'])
        result['warning'] = bool(result['warning'])
        result['deposit_amount_soaring'] = bool(result['deposit_amount_soaring'])
        result['global_price_differences'] = bool(result['global_price_differences'])
        result['price_fluctuations'] = bool(result['price_fluctuations'])
        result['trading_volume_soaring'] = bool(result['trading_volume_soaring'])
        result['concentration_of_small_accounts'] = bool(result['concentration_of_small_accounts'])

        return result