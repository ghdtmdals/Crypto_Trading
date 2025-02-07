from typing import List
import datetime
from pytz import timezone
from Data.News.news_crawling import NewsCrawling

class CoinPress(NewsCrawling):
    # @staticmethod
    # def af_get_news_data(coin_name, token):
    #     source = 'coinpress'
    #     params = {"s": coin_name}
    #     url = "https://coinspress.com/"
    #     return super().af_get_news_data(token, source, url, params, \
    #                                     title_block_tag = 'div', title_block_class_name = "col-12 order-3 order-md-2 col-md-4", \
    #                                     title_tag = 'h2', title_class_name = "post-title", \
    #                                     date_tag = 'li', date_class_name = "list-inline-item post-date")
    
    def __init__(self, coin_name: str, token: str):
        self.coin_name = coin_name
        self.token = token
        self.params = {"s": self.coin_name} ### Ex) Bitcoin
        self.url = "https://coinspress.com/"
        self.source = 'coinpress'
        self.current_date = None
    
    def __call__(self) -> List[tuple]:
        self.current_date = datetime.datetime.now(timezone('Asia/Seoul'))
        return self.get_news_data(title_block_tag = 'div', title_block_class_name = "col-12 order-3 order-md-2 col-md-4", \
                           title_tag = 'h2', title_class_name = "post-title", \
                           date_tag = 'li', date_class_name = "list-inline-item post-date")