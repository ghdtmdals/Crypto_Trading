from Data.News.coinpedia import CoinPedia
from Data.News.coinpress import CoinPress
from Data.Upbit.upbit_data import UpbitPrice

class DataCrawler:
    def __init__(self, coin_name: str):
        self.coinpedia = CoinPedia(coin_name = coin_name)
        self.coinpress = CoinPress(coin_name = coin_name)
        self.upbit = UpbitPrice(coin_name = coin_name)
        self.token = self.upbit.token
    
    ### 호출 시점이 다르기 때문에 따로따로 호출
    def get_news_data(self):
        ### 호출 빈도가 낮기 때문에 호출이 정상적으로 이뤄지고 있음을 출력
        print("Collecting News Data")
        self.coinpedia()
        self.coinpress()
    
    def get_price_data(self):
        self.upbit()