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

        ### Add New Sources
        self.news = [CoinPedia(self.coin_name, self.token), CoinPress(self.coin_name, self.token)]
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()

    ### DB 테이블 생성
    def create_tables(self) -> None:
        with open("./Database/create_tables.sql", "r") as f:
            sql = f.read()
        self.cursor.execute(sql)
        self.conn.reconnect()
    
    def get_token(self) -> str:
        query = f"SELECT token FROM Crypto_Info WHERE english_name = '{self.coin_name}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result[0]['token'] ### [(token, )]

    ### DB에서 COLUMN 별 데이터 타입 받은 다음에 길이 비교
    ### DECIMAL, VARCHAR만 확인하면 됨
    ### input_data: List[tuple] || tuple
    def check_data_type(self, input_data, table_name: str) -> None:
        query = "SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE " \
                + f"FROM information_schema.COLUMNS WHERE 1=1 AND TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION;"
        self.cursor.execute(query)
        data_table = self.cursor.fetchall()

        if type(input_data) is not list:
            input_data = [input_data]

        ### INT 자료형은 범위를 벗어나지 않는 한 조절할 필요 없음
        ### 나머지 자료형도 범위를 조절할 필요는 없음
        ### varchar 타입 COLUMN과 decimal 타입 COLUMN 탐색
        ### List 데이터일 경우 특정 컬럼의 최대값을 찾은 다음에 해당 값을 기준으로 판단하는 것 보다
        ### 매번 데이터를 확인하면서 데이터가 입력 가능한 길이를 초과하는지 확인 -> 어차피 최대값 찾는것도 모든 데이터를 한 번은 훑어야 함
        for data in input_data:
            for i in range(len(data_table)):
                if data_table[i]['DATA_TYPE'] == 'varchar':
                    ### 입력할 텍스트 길이 + 1이 제한 길이보다 길 경우 제한 길이를 입력할 텍스트 길이 + 1로 변경
                    if len(data[i]) + 1 > data_table[i]['CHARACTER_MAXIMUM_LENGTH']:
                        length = len(data[i]) + 1
                        query = f"ALTER TABLE {table_name} MODIFY COLUMN {data_table[i]['COLUMN_NAME']} VARCHAR({length})"
                        self.cursor.execute(query)
                    
                elif data_table[i]['DATA_TYPE'] == 'decimal':
                    temp_float = str(round(data[i], data_table[i]['NUMERIC_SCALE']))
                    ### 소수점 포함 숫자 자릿수가 제한 자릿수보다 클 경우 변경
                    if len(temp_float) > data_table[i]['NUMERIC_PRECISION']:
                        length = len(temp_float) + 1
                        query = f"ALTER TABLE {table_name} MODIFY COLUMN {data_table[i]['COLUMN_NAME']} DECIMAL({length}, {data_table[i]['NUMERIC_SCALE']})"
                        self.cursor.execute(query)
    
    ### 일정 주기로 호출되도록 설정
    def collect_crypto_info(self) -> None:
        print("Checking for Newly Listed Crypto Information")
        url = "https://api.upbit.com/v1/market/all"
        resp = requests.get(url)

        ### BTC-ETH와 같이 비트코인이 화폐단위인 경우도 있음
        ### KRW로 시작하는 토큰만 추출
        crypto_info = []
        for crypto in resp.json():
            if crypto["market"].startswith("KRW"):
                crypto_info.append((crypto['market'], crypto['english_name'], crypto['korean_name']))

        self.check_data_type(crypto_info, 'Crypto_Info')
        
        query = "INSERT IGNORE INTO Crypto_Info (token, english_name, korean_name) VALUES (%s, %s, %s);"
        self.cursor.executemany(query, crypto_info)
        self.conn.commit()

    def save_price_data(self) -> None:
        data = self.upbit()
        self.check_data_type(data, 'Upbit')

        query = "INSERT INTO Upbit (" \
                + "token, trade_date_kst, trade_time_kst, high_price, low_price, opening_price, trade_price, signed_change_rate, " \
                + "warning, deposit_amount_soaring, global_price_differences, price_fluctuations, " \
                + "trading_volume_soaring, concentration_of_small_accounts" \
                + ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, data)
        self.conn.commit()

    def save_news_data(self) -> None:
        for news in self.news:
            print(f"Collecting {news.coin_name} News Data From {news.source}")
            data = news()
            self.check_data_type(data, 'News')

            query = "INSERT IGNORE INTO News (token, news_date, news_source, title, sentiment) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.executemany(query, data)
            self.conn.commit()
    
    def save_log_data(self, *data) -> None:
        log = (self.token, str(data[0].date()), str(data[0].time()), 
               data[1]['krw_balance'], data[1]['token_balance'], data[2], json.dumps(data[3]))
        self.check_data_type(log, 'Trade_Log')

        query = "INSERT INTO Trade_Log (" \
                + "token, trade_date, trade_time, krw_balance, token_balance, trade_call, trade_result" \
                + ") VALUES(%s, %s, %s, %s, %s, %s, %s)"
        
        self.cursor.execute(query, log)
        self.conn.commit()

    def load_data(self, sentiment_days: int = 1, sentiment_type: str = 'all') -> dict:
        sentiment_types = {'all': 'SENTIMENT_RATIO',
                           'pos_neg': 'POS_NEG_RATIO',
                           'avg': 'AVG_SENTIMENT'}
        query = "SELECT * " \
                + "FROM " \
                + f"(SELECT token, {sentiment_types[sentiment_type]}({sentiment_days}) AS sentiment " \
                + "FROM News " \
                + "ORDER BY news_date DESC " \
                + "LIMIT 1) S " \
                + "INNER JOIN Upbit U ON S.token = U.token " \
                + f"WHERE S.token = '{self.token}' " \
                + "ORDER BY U.trade_date_kst DESC, U.trade_time_kst DESC " \
                + "LIMIT 1;"
        
        self.cursor.execute(query)
        result = self.cursor.fetchall()[0]

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