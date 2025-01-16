import torch
from Model.Network.trade_nets import TradeNetBasic

class ModelTrainer:
    def __init__(self):
        self.model = None
        self.criterion = None
        self.optimizer = None
        
    
    def train_setup(self, model, learning_rate):
        self.model = model
        self.criterion = torch.nn.CrossEntropyLoss()
        self.scaler = torch.cuda.amp.GradScaler()

        ### Default: betas=(0.9, 0.999), eps=1e-08, weight_decay=0.01
        self.optimizer = torch.optim.AdamW(params = self.model.trader_layers.parameters(), lr = learning_rate)

    def train(self, output, target):
        loss = self.criterion(output, target)
        self.scaler.scale(loss).backward()
        self.scaler.step(self.optimizer)
        self.scaler.update()


    def eval(self):
        ### If Evaluated Acc >= 0.7, Start Actual Trading
        pass

    def save_model(self):
        pass

    def load_model(self):
        pass

class TradeStrategy:
    def __init__(self, algorithm: str = 'test'):
        self.algorithm = algorithm
        self.models = {
            'test': self.test_strategy,
            'basic': TradeNetBasic,
        }
        if algorithm == 'test':
            self.model = self.models[self.algorithm]
        else:
            ### 딥러닝 모델을 활용하는 경우 init 시점에 모델을 초기화해야 함
            self.calls = ['bid', 'hold', 'ask']
            self.model = self.models[self.algorithm]().train()

    def __call__(self, data: dict, image: torch.Tensor, balance: dict) -> str:
        if self.algorithm == 'test':
            output = self.model(data, balance)
        else:
            output = self.model_strategy(data, image, balance)
        return output

    def test_strategy(self, data: dict, balance: dict) -> str:
        ### 매수 or 매도할 비중, 전략에 따라 분할매수 할 수 있기 때문에 반환값 일관성 목적으로 설정

        ### data = {prices, events, krw_balance, token_balance}
        ### KRW 주문 가능 (최소주문금액 5000원) + 하락하면 매수
        if (balance['krw_balance'] > 5000) and (data['signed_change_rate'] < -0.01):
            decision = 'bid'
        ### 토큰 잔고 있음 + 상승하면 매도
        elif (balance['token_balance'] > 0) and data['signed_change_rate'] > 0.05:
            decision = 'ask'
        ### change가 정확이 0일수는 없기 때문에 임의로 -0.01 ~ 0.01 범위를 Hold 지점으로 설정
        else:
            decision = 'hold'
        
        return decision
    
    def model_strategy(self, data: dict, image: torch.Tensor, balance: dict) -> str:
        output = self.model(image, data)
        output = output.argmax()

        if (balance['krw_balance'] > 5000):
            decision = self.calls[output]
        elif (balance['krw_balance'] <= 5000 and self.calls[output] == 'bid'):
            decision = 'hold'
        else:
            decision = self.calls[output]
        
        return decision
