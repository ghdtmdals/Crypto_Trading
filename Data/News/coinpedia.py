import datetime
from pytz import timezone
from Data.News.news_crawling import NewsCrawling

class CoinPedia(NewsCrawling):
    def __init__(self, coin_name: str):
        ### NewsCrawling 클래스의 인스턴스 속성을 모두 초기화하기 때문에 별도로 부모 클래스를 초기화 할 필요 없음
        self.coin_name = coin_name
        self.params = {"s": self.coin_name} ### Ex) Bitcoin
        self.url = "https://coinpedia.org/"
        self.source = 'coinpedia'
        self.current_date = None

    def __call__(self) -> None:
        self.current_date = datetime.datetime.now(timezone('Asia/Seoul'))
        self.save_data(title_block_tag = 'div', title_block_class_name = "post-details", \
                       title_tag = 'h2', title_class_name = "post-title", \
                       date_tag = 'span', date_class_name = "date meta-item tie-icon")