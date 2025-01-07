import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class Sentiment:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name).eval().to(self.device)

    def get_sentiment(self, text: str):
        text = self.tokenizer(text, return_tensors = "pt").to(self.device) ### Pytorch: "pt", Tensorflow: "tf", Numpy: "np"

        with torch.no_grad():
            output = self.model(**text).logits
        
        return output.argmax().item() ### 0: Negative, 1: Neutral, 2: Positive