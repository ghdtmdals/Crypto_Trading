### Power BI Script for Data Load and Transform

### pip install sqlalchemy pymysql pandas scikit-learn
from sqlalchemy import create_engine
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import multiprocessing
import datetime
from tqdm import tqdm

engine = create_engine("mysql+pymysql://root:1111@192.168.0.2/crypto_db")
conn = engine.connect()

query = "SELECT token, trade_date, trade_time, krw_balance, token_balance, trade_call, target FROM Trade_Log;"

df = pd.read_sql(query, conn)

date_time = []
for date, time in zip(df['trade_date'], df['trade_time']):
    time_value = (datetime.datetime.min + time).time()
    date_time.append(datetime.datetime.combine(date, time_value))

df['date_time'] = date_time

df = df.drop('trade_date', axis = 1)
df = df.drop('trade_time', axis = 1)

df['24h_accuracies'] = 0
df['24h_precision'] = 0
df['24h_recall'] = 0
df['24h_f1'] = 0

df = df.astype({'24h_accuracies': 'float32', '24h_precision': 'float32',
                '24h_recall': 'float32', '24h_f1': 'float32'})

# if __name__ == "__main__" :
#     multi_function(some_function, global_list, use_ratio)
def multi_function(exec_function, data, use_ratio: float = 0.5):
    n_cpu = int(multiprocessing.cpu_count() * use_ratio)
    full_len = len(data) # data count
    process_index = int(full_len / n_cpu) # split counts
    rng_list = [(i + 1) * process_index for i in range(n_cpu)] # split indicies
    rng_list[-1] = full_len
    if rng_list[0] != 0:  # add 0 on first index
        rng_list.insert(0, 0)
    if rng_list[-1] < full_len: # last element of range list should equal to data length
        rng_list.append(full_len)

    manager = multiprocessing.Manager()
    return_list = manager.list()

    procs = []
    for i in range(len(rng_list) - 1):
        p = multiprocessing.Process(target = exec_function, args = (rng_list[i], rng_list[i + 1], return_list))
        p.start()
        procs.append(p)
    
    for p in procs:
        p.join()
    
    return return_list

def calculate_metrics(start, end, return_list):
    for i in tqdm(range(start, end)):
        time = df['date_time'][i]
        last_24h = time - datetime.timedelta(hours = 24)
        last_24h = last_24h.replace(second = 0) ### 초 단위는 버림
        sub_df = df[(time >= df['date_time']) & (df['date_time'] >= last_24h)] ### 24시간 거래 로그
        if len(sub_df) >= 3: ### 거래 로그가 24시간 * 60분 개 (하루치 로그) 발생하지 않은 경우 계산하지 않음
            df.loc[i, '24h_accuracies'] = round(accuracy_score(sub_df['target'], sub_df['trade_call']), 3)
            df.loc[i, '24h_precision'] = round(precision_score(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0), 3)
            df.loc[i, '24h_recall'] = round(recall_score(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0), 3)
            df.loc[i, '24h_f1'] = round(f1_score(sub_df['target'], sub_df['trade_call'], average = 'weighted', zero_division = 1.0), 3)
    return return_list.append(df[start:end])

if __name__ == "__main__":
    start = datetime.datetime.now()
    
    results = multi_function(calculate_metrics, df, use_ratio = 0.7)
    df = pd.concat(results, axis = 0).sort_index()
    print(df)

    end = datetime.datetime.now()

    print(end - start)

    conn.close()