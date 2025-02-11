import os
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import datetime
from Model.Network.trade_nets import TradeNetBasic

class ModelTrainer:
    def __init__(self, learning_rate: float = 1e-5):
        self.algorithm = None
        self.model = None
        self.token = None
        self.calls = None
        self.output = None
        self.learning_rate = learning_rate

        self.ckpnt_root = "./Model/checkpoints/"
        self.optimizer = None
        self.criterion = None
        self.scaler = None
    
    def get_target(self, change_rate: float, avg_change_rate: float) -> torch.Tensor:
        if change_rate > avg_change_rate: return torch.Tensor([2]).type(torch.uint8) # ask
        if change_rate < -avg_change_rate: return torch.Tensor([0]).type(torch.uint8) # bid
        return torch.Tensor([1]).type(torch.uint8) # hold
    
    def train_setup(self) -> None:
        self.ckpnt_root = "./Model/checkpoints/"
        self.load_model()

        ### Default: betas=(0.9, 0.999), eps=1e-08, weight_decay=0.01
        self.optimizer = torch.optim.AdamW(params = self.model.trader_layers.parameters(), lr = self.learning_rate)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.scaler = torch.cuda.amp.GradScaler() ### FP16
    
    def train(self, target) -> None:
        if self.algorithm != "test":
            with torch.cuda.amp.autocast():
                loss = self.criterion(self.output, target)
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
            self.save_model()

    def eval(self, trade_logs) -> None:
        preds = []
        targets = []
        for log in trade_logs:
            preds.append(log['trade_call'])
            targets.append(log['target'])

        scores = {"avg_accuracy": round(accuracy_score(targets, preds), 3),
                  "avg_precision": round(precision_score(targets, preds, average = 'weighted', zero_division = 1.0), 3),
                  "avg_recall": round(recall_score(targets, preds, average = 'weighted', zero_division = 1.0), 3),
                  "avg_f1": round(f1_score(targets, preds, average = 'weighted', zero_division = 1.0), 3)}
        
        eval_str = f"Avg Acc = {scores['avg_accuracy']} | " \
                  + f"Avg Precision = {scores['avg_precision']} | " \
                  + f"Avg Recall = {scores['avg_recall']} | " \
                  + f"Avg F1 Score = {scores['avg_f1']}"
        print(eval_str)

        return scores
    
    def get_accuracy(self, trade_logs) -> float:
        preds = []
        targets = []
        for log in trade_logs:
            preds.append(log['trade_call'])
            targets.append(log['target'])
        
        return accuracy_score(targets, preds)

    def save_model(self) -> None:
        if not os.path.isdir(self.ckpnt_root):
            os.mkdir(self.ckpnt_root)
        
        now = str(datetime.datetime.now().date())
        torch.save({"model_state_dict": self.model.trader_layers.state_dict(),
                    'updated': now},
                   f"{self.ckpnt_root}{self.token}.pt")

    def load_model(self) -> None:
        ckpnt_path = f"{self.ckpnt_root}{self.token}.pt"
        if os.path.isfile(ckpnt_path):
            self.model.trader_layers.load_state_dict(torch.load(ckpnt_path)['model_state_dict'])

class TradeStrategy(ModelTrainer):
    def __init__(self, token: str, algorithm: str = 'test', learning_rate: float = 1e-5):
        super(TradeStrategy, self).__init__(learning_rate)

        self.token = token
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
            self.train_setup()

    def __call__(self, data: dict, image: torch.Tensor, target) -> str:
        if self.algorithm == 'test':
            call = self.model(data)
        else:
            call = self.model_strategy(data, image, target)
        return call

    def test_strategy(self, data: dict) -> str:
        ### 하락하면 매수
        if data['signed_change_rate'] < -0.01:
            decision = 'bid'
        ### 상승하면 매도
        elif data['signed_change_rate'] > 0.05:
            decision = 'ask'
        ### change가 정확이 0일수는 없기 때문에 임의로 -0.01 ~ 0.01 범위를 Hold 지점으로 설정
        else:
            decision = 'hold'
        
        return decision
    
    def model_strategy(self, data: dict, image: torch.Tensor, target) -> str:
        self.output = self.model(image, data)
        target = target.to(self.model.device)
        self.train(target)

        self.output = self.output.argmax()

        return self.calls[self.output]
