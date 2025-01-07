import os
import keys
from Trade.trade import Trader

### DB 로드와 같은 작업 수행
### Database 폴더가 없으면 생성

def main(*token):
    os.environ["UPBIT_OPEN_API_ACCESS_KEY"] = keys.UPBIT_ACCESS_KEY
    os.environ["UPBIT_OPEN_API_SECRET_KEY"] = keys.UPBIT_SECRET_KEY

    if len(token) == 1:
        single_token_trade(token)
    else:
        multi_token_trade(token)

def single_token_trade(token): 
    trader = Trader(token[0])
    trader.start_trading()

def multi_token_trade(token): 
    ### multiprocessing으로 여러개 동시 실행
    print(token)

if __name__ == "__main__":
    main('Bitcoin')