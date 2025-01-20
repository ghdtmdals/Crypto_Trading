import clip
import torch
from torch import nn

class TradeNetBasic(nn.Module):
    def __init__(self):
        super(TradeNetBasic, self).__init__()
        self.drop_p = 0.5
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.clip_model, __preprocess = clip.load("ViT-B/32", device = self.device)
        ### CLIP의 파라미터는 업데이트 X, fusion layer와 classifier만 학습
        self.trader_layers = nn.Sequential(self.fusion_layer(),
                                           self.classifier())
        ### CLIP과 동일하게 dtype float16으로 맞춰줌, Backward Propagation에는 Scaler 사용해서 Gradient 0 방지
        self.trader_layers = self.trader_layers.to(self.device)
        # .type(torch.float16)
    
    @torch.cuda.amp.autocast()
    def forward(self, image, price_data):
        texts = []
        for k, v in price_data.items():
            texts.append(f"{k}: {v}")
        
        texts = clip.tokenize(texts).to(self.device)
        image = image.unsqueeze(0).to(self.device)
        
        texts = self.clip_model.encode_text(texts)
        text = torch.sum(texts, dim = 0).unsqueeze(0)
        image = self.clip_model.encode_image(image)

        concat = torch.concat([text, image], dim = -1)
        output = self.trader_layers(concat)

        return output

    def fusion_layer(self):
        return nn.Sequential(nn.Linear(1024, 1024, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU(),
                             nn.Linear(1024, 2048, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU(),
                             nn.Linear(2048, 1024, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU(),
                             nn.Linear(1024, 512, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU())

    def classifier(self):
        return nn.Sequential(nn.Linear(512, 1024, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU(),
                             nn.Linear(1024, 1024, bias = True),
                             nn.Dropout(self.drop_p),
                             nn.ReLU(),
                             nn.Linear(1024, 3, bias = True)) ### bid, ask, hold