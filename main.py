from Trade.trade import Trader

def main(*token):
    if len(token) == 1:
        single_token_trade(token)
    else:
        multi_token_trade(token)

def single_token_trade(token): 
    trader = Trader(token[0])
    trader.start_trading()

def multi_token_trade(token): 
    ### multiprocessing으로 여러개 동시 실행
    pass

if __name__ == "__main__":
    main('Bitcoin')