### Power BI Script for Data Load and Transform

### pip install pymysql pandas scikit-learn
import pymysql
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


### Example
# data = [['Alex',20],['Bob',12],['Clarke',13]]
# df = pd.DataFrame(data,columns=['Name','Age'])
# print (df)

conn = pymysql.connect(
                        host = 'REMOTE_DB_HOST',
                        user = "USER_NAME",
                        password = "USER_PASSWORD",
                        database = "crypto_db",
                    )

query = "SELECT token, trade_date, trade_time, krw_balance, token_balance, trade_call, target FROM Trade_Log ORDER BY trade_date DESC, trade_time DESC LIMIT 5;"

df = pd.read_sql(query, conn)

print(df[df['trade_date'] == '2025-02-17'])


# scores = {"avg_accuracy": round(accuracy_score(targets, preds), 3),
#                   "avg_precision": round(precision_score(targets, preds, average = 'weighted', zero_division = 1.0), 3),
#                   "avg_recall": round(recall_score(targets, preds, average = 'weighted', zero_division = 1.0), 3),
#                   "avg_f1": round(f1_score(targets, preds, average = 'weighted', zero_division = 1.0), 3)}

print(df)