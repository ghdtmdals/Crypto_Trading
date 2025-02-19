### cron setup
### */15 * * * * docker exec metrics_calculator python /workspace/metrics_calculation.py

### Power BI Script for Data Load and Transform

import os
from sqlalchemy import create_engine
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import datetime
# from tqdm import tqdm


def set_connection():
    mysql_user = os.environ['MYSQL_USER']
    mysql_password = os.environ['MYSQL_PASSWORD']
    mysql_host = "remote_mysql:3306"
    mysql_db = os.environ['MYSQL_DATABASE']

    engine = create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
    conn = engine.connect()
    return engine, conn

def read_log_table(conn):
    query = \
    """
    SELECT token, 
    STR_TO_DATE(CONCAT(trade_date, " ", trade_time), "%%Y-%%m-%%d %%H:%%i:%%s") AS trade_datetime,
    krw_balance, token_balance,
    trade_call, target
    FROM Trade_Log;
    """

    df = pd.read_sql(query, conn)

    return df

def add_metrics(df):
    df['24h_accuracies'] = 0.0
    df['24h_precision'] = 0.0
    df['24h_recall'] = 0.0
    df['24h_f1'] = 0.0
    
    return df

def update_metrics(df):
    start = 0
    for i in range(len(df)):
        ### 하루 분량의 로그 이후부터 계산
        if i > (60 * 24):
            sub_df = df[start:i]

            df.loc[i, '24h_accuracies'] = round(accuracy_score(sub_df['target'], sub_df['trade_call']), 3)
            precision, recall, f1, _ = precision_recall_fscore_support(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0)
            df.loc[i, '24h_precision'] = round(precision, 3)
            df.loc[i, '24h_recall'] = round(recall, 3)
            df.loc[i, '24h_f1'] = round(f1, 3)
            
            start += 1
    return df

def update_table(df, engine):
    df.to_sql(name = "clsf_metrcis", con = engine, if_exists = "replace", index = False)

if __name__ == "__main__":
    engine, conn = set_connection()

    log_df = read_log_table(conn)
    log_df = add_metrics(log_df)
    log_df = update_metrics(log_df)
    
    update_table(log_df, engine)

    print(log_df)

    conn.close()