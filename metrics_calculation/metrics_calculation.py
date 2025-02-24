### cron setup
### */15 * * * * docker exec metrics_calculator python /workspace/metrics_calculation.py

### Power BI Script for Data Load and Transform

import os
from sqlalchemy import create_engine
import pandas as pd
from custom_metrics import *
from sklearn.metrics import accuracy_score
# import datetime
# from tqdm import tqdm


def set_connection():
    mysql_user = os.environ['MYSQL_USER']
    mysql_password = os.environ['MYSQL_PASSWORD']
    mysql_host = "remote_mysql:3306"
    mysql_db = os.environ['MYSQL_DATABASE']

    engine = create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
    return engine

def read_log_table(conn):
    check_table_exists_query = 'SHOW TABLES;'
    table_list = pd.read_sql(check_table_exists_query, conn)

    if "clsf_metrics" in table_list['Tables_in_crypto_db'].to_list():
        query = 'SELECT L.token, L.trade_datetime, L.krw_balance, L.token_balance, L.trade_call, L.target, ' \
                + 'IFNULL(C.24h_accuracies, 0) AS 24h_accuracies, IFNULL(C.24h_precision, 0) AS 24h_precision, ' \
                + 'IFNULL(C.24h_recall, 0) AS 24h_recall, IFNULL(C.24h_f1, 0) AS 24h_f1 ' \
                + 'FROM (' \
                + 'SELECT *, STR_TO_DATE(CONCAT(trade_date, " ", trade_time), "%%Y-%%m-%%d %%H:%%i:%%s") AS trade_datetime ' \
                + 'FROM Trade_Log) L ' \
                + 'LEFT JOIN (' \
                + 'SELECT * FROM clsf_metrics) C ' \
                + 'ON L.trade_datetime = C.trade_datetime ' \
                + 'ORDER BY L.trade_datetime ASC;'
        
    else:
        query = 'SELECT token, ' \
                + 'STR_TO_DATE(CONCAT(trade_date, " ", trade_time), "%%Y-%%m-%%d %%H:%%i:%%s") AS trade_datetime, ' \
                + 'krw_balance, token_balance, trade_call, target ' \
                + 'FROM Trade_Log ' \
                + 'ORDER BY trade_datetime ASC;'

    df = pd.read_sql(query, conn)

    return df

def add_metrics(df):
    if '24h_accuracies' not in df.columns:
        df['24h_accuracies'] = 0.0
        df['24h_precision'] = 0.0
        df['24h_recall'] = 0.0
        df['24h_f1'] = 0.0
    
    return df

# def dep_update_metrics(df):
#     start = 0
#     for i in tqdm(range(len(df))):
#         ### 하루 분량의 로그 이후부터 계산
#         if i > (60 * 24):
#             if df.loc[i, '24h_accuracies'] == 0.0:
#                 sub_df = df[start:i]

#                 df.loc[i, '24h_accuracies'] = round(accuracy_score(sub_df['target'], sub_df['trade_call']), 3)
#                 precision, recall, f1, _ = precision_recall_fscore_support(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0)
#                 df.loc[i, '24h_precision'] = round(precision, 3)
#                 df.loc[i, '24h_recall'] = round(recall, 3)
#                 df.loc[i, '24h_f1'] = round(f1, 3)
                
#             start += 1
#     return df

def update_metrics(df):
    start = 0
    for i in range(len(df)):
        if i > (60 * 24):
            if df.loc[i, '24h_accuracies'] == 0.0:
                break
            start += 1
    
    sub_df = df[start:i] ### Up to Records WITH Calculated Metrics (EXCLUDING i), Need to Calculate i, That is, i = t+1
    sub_df = sub_df.reset_index(drop = True)

    labels = ['bid', 'hold', 'ask']
    cm_t, r0, sub_df = create_confusion_matrix(sub_df, labels) #### CM_t

    ### Loop
    for j in range(i, len(df)):
        ### Include R_t+1
        t1 = df.loc[j]
        cm_t, r0, sub_df = update_confusion_matrix(t1, r0, cm_t, sub_df, labels)
        precision, recall, f1 = custom_precison_recall_fscore(cm_t, labels)

        ### sklearn.metrics.accuracy_score does not use confusion matrix based calculation
        df.loc[j, '24h_accuracies'] = round(accuracy_score(sub_df['target'], sub_df['trade_call']), 3)
        df.loc[j, '24h_precision'] = precision
        df.loc[j, '24h_recall'] = recall
        df.loc[j, '24h_f1'] = f1
    
    return df

def update_table(df, engine):
    df.to_sql(name = "clsf_metrics", con = engine, if_exists = "replace", index = False)

if __name__ == "__main__":
    engine = set_connection()
    conn = engine.connect()

    log_df = read_log_table(conn)
    conn.close()

    log_df = add_metrics(log_df)

    log_df = update_metrics(log_df)

    # start = datetime.datetime.now()
    # end = datetime.datetime.now()
    # print("Optimized Loop Time Elapsed: ", (end - start))

    conn = engine.connect()
    update_table(log_df, engine)
    conn.close()

    # print(log_df)

    engine.dispose()