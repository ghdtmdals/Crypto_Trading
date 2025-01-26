from contextlib import contextmanager
from Trade.trade import Trader
import time
import os
import sys

### Pytorch 컨테이너 사용
### pip install transformers PyJWT python-dateutil mysql-connector-python

def main(*token):
        if len(token) == 1:
            with auto_restart(token[0], Exception):
                single_token_trade(token)
        else:
            with auto_restart(token, Exception):
                multi_token_trade(token)

def single_token_trade(token):
    trader = Trader(token[0], trade_portion = 1.0)
    trader.start_trading()

def multi_token_trade(token): 
    ### multiprocessing으로 여러개 동시 실행
    print(token)

@contextmanager
def auto_restart(token, *exceptions):
    try:
        yield
    except exceptions as e:
        print(e)
        time.sleep(10)
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    main('Bitcoin')