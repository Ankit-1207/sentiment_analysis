# ---------------- SAFE IMPORT ----------------
import os
import re

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Mute TF warnings

# Try loading DL model safely
try:
    from dl_model import predict_sentiment as lstm_predict
    MODEL_AVAILABLE = True
except Exception as e:
    print("DL model not available:", e)
    MODEL_AVAILABLE = False


# ---------------- KEYWORDS ----------------
ABUSIVE_KEYWORDS = [
    "chutiya", "madarchod", "behenchod", "bhadwe", "gandu",
    "bitch", "fuck", "asshole", "mc", "bc", "lodu", "bsdk",
    "scam", "die", "kill", "suicide", "kys", "death", "murder"
]

NEGATIVE_KEYWORDS = [
    "ew", "eww", "ewww", "yuck", "gross", "disgusting",
    "hate", "ugly", "bad", "terrible", "awful", "worst",
    "trash", "garbage", "cringe", "fake", "boring"
]


# ---------------- MAIN FUNCTION ----------------
def predict_sentiment(text):
    text_str = str(text).lower()

    # ---------- 1. Abusive Override ----------
    for word in ABUSIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_str):
            return "abusive"

    # ---------- 2. Negative Override ----------
    for word in NEGATIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', text_str):
            return "negative"

    # ---------- 3. Deep Learning Model ----------
    if MODEL_AVAILABLE:
        try:
            sentiment = lstm_predict(text_str)
            return sentiment
        except Exception as e:
            print(f"DL Prediction Error: {e}")

    # ---------- 4. Fallback ----------
    return "neutral"