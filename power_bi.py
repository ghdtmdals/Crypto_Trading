### Power BI Script for Data Load and Transform

### pip install sqlalchemy pymysql pandas scikit-learn
import pymysql
# from pymysql.constants import CLIENT
from sqlalchemy import create_engine
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import datetime
from tqdm import tqdm


################################################################################
############################# Working With Pymysql #############################
################################################################################

conn = pymysql.connect(
                host = 'remote_mysql',
                port = 3306,
                user = "root",
                password = "1111",
                database = "crypto_db",
                # client_flag = CLIENT.MULTI_STATEMENTS
            )
cursor = conn.cursor(pymysql.cursors.DictCursor)

query = \
"""
CREATE VIEW IF NOT EXISTS Result_Metrics AS
SELECT token, 
STR_TO_DATE(CONCAT(trade_date, " ", trade_time), "%Y-%m-%d %H:%i:%s") AS trade_datetime,
krw_balance, token_balance,
trade_call, target
FROM Trade_Log;
"""

cursor.execute(query)

conn.close()

################################################################################
############################# Pymysql Finish ###################################
################################################################################





#################################################################################
############################## Metrics Calculation ##############################
#################################################################################

engine = create_engine("mysql+pymysql://root:1111@remote_mysql:3306/crypto_db")
conn = engine.connect()

query = "SELECT * FROM Result_Metrics;"

df = pd.read_sql(query, conn)

df['24h_accuracies'] = 0.0
df['24h_precision'] = 0.0
df['24h_recall'] = 0.0
df['24h_f1'] = 0.0

min_log_length = ((60 * 24) + (60 * 12)) / 2 ### ((하루 분량) + (반나절 분량)) / 2
for i in tqdm(range(len(df))):
    time = df['trade_datetime'][i]
    last_24h = time - datetime.timedelta(hours = 24)
    last_24h = last_24h.replace(second = 0) ### 초 단위는 버림
    sub_df = df[(time >= df['trade_datetime']) & (df['trade_datetime'] >= last_24h)] ### 24시간 거래 로그

    ### 거래 로그가 하루 분량과 반나절 분량의 평균 이상으로 발생한 경우만 계산
    ### 분 단위로 자동매매가 실행되지만 데이터 호출 등의 사전 작업으로 정확히 1분 간격으로 로그가 발생하지 않음
    if len(sub_df) >= min_log_length:
        df.loc[i, '24h_accuracies'] = round(accuracy_score(sub_df['target'], sub_df['trade_call']), 3)
        precision, recall, f1, _ = precision_recall_fscore_support(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0)
        df.loc[i, '24h_precision'] = round(precision, 3)
        df.loc[i, '24h_recall'] = round(recall, 3)
        df.loc[i, '24h_f1'] = round(f1, 3)

print(df)

conn.close()