class TradeStrategy:
    def __init__(self, algorithm: str = 'test'):
        self.algorithm = algorithm
        self.strategies = {
            'test': self.test_strategy
        }

    def __call__(self, data: dict) -> str:
        output = self.strategies[self.algorithm](data)
        return output

    def test_strategy(self, data: dict) -> list:
        ### 매수 or 매도할 비중, 전략에 따라 분할매수 할 수 있기 때문에 반환값 일관성 목적으로 설정
        balance_portion = 1.0

        ### data = {prices, events, krw_balance, token_balance}
        ### KRW 주문 가능 (최소주문금액 5000원) + 하락하면 매수
        if (data['krw_balance'] > 5000) and (data['signed_change_rate'] < -0.01):
            decision = 'bid'
        ### 토큰 잔고 있음 + 상승하면 매도
        elif (data['token_balance'] > 0) and data['signed_change_rate'] > 0.05:
            decision = 'ask'
        ### change가 정확이 0일수는 없기 때문에 임의로 -0.01 ~ 0.01 범위를 Hold 지점으로 설정
        else:
            decision = 'hold'
        
        return [decision, balance_portion]
