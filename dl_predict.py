# Fallback due to PyTorch not downloading.
# Utilizing User's Trained Deep Learning Tensor Model (sentiment_dl_model.h5)
import os
import re

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Mute TF warnings
from dl_model import predict_sentiment as lstm_predict

ABUSIVE_KEYWORDS = ["chutiya", "madarchod", "behenchod", "bhadwe", "gandu", "bitch", "fuck", "asshole", "mc", "bc", "lodu", "bsdk", "scam", "die", "kill", "suicide", "kys", "death", "murder"]
NEGATIVE_KEYWORDS = ["ew", "eww", "ewww", "yuck", "gross", "disgusting", "hate", "ugly", "bad", "terrible", "awful", "worst", "trash", "garbage", "cringe", "fake", "boring"]

def predict_sentiment(text):
    text_str = str(text).lower()
    
    # 1. Abusive Keyword Overrides
    for word in ABUSIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_str):
            return "abusive"

    # 1.5. Negative Keyword Overrides
    for word in NEGATIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_str):
            return "negative"

    # 2. Local Custom DL Model (TensorFlow LSTM)
    try:
        sentiment = lstm_predict(text_str) 
        # lstm_predict returns "positive", "negative", or "neutral"
        return sentiment
    except Exception as e:
        print(f"Deep Learning Model Error: {e}")
        return "neutral"