import requests
import bs4
from bs4 import BeautifulSoup
import json
from typing import List

class GoogleNews:
    def __init__(self):
        ### 영어 + 한국어 뉴스 수집
        kr_url = None
        en_url = None

    def get_response(self, url: str, n_pages: int) -> List[bs4.element.ResultSet]:
        ### google news에서 호출
        pass

    def get_titles(self, resp: BeautifulSoup) -> List[str]:
        ### 뉴스 타이틀만 호출
        pass

    def save_data(self, titles: List[str]) -> None:
        pass