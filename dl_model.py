import pickle
import re
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ---------------- LOAD MODEL SAFELY ----------------
try:
    model = load_model("sentiment_dl_model.h5")
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    MODEL_LOADED = True
except Exception as e:
    print("Model loading failed:", e)
    MODEL_LOADED = False

# ---------------- KEYWORD LIST ----------------
positive_words = [
    "good", "great", "amazing", "love", "awesome", "nice", "best", "happy"
]

negative_words = [
    "bad", "worst", "terrible", "hate", "awful", "ugly", "stupid", "trash", "die"
]

# ---------------- TEXT CLEANING ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.strip()

# ---------------- MAIN PREDICTION FUNCTION ----------------
def predict_sentiment(text):

    text = clean_text(text)

    # ---------- KEYWORD OVERRIDE (FAST + IMPORTANT) ----------
    for word in negative_words:
        if word in text:
            return "negative"

    for word in positive_words:
        if word in text:
            return "positive"

    # ---------- DEEP LEARNING MODEL ----------
    if MODEL_LOADED:
        try:
            seq = tokenizer.texts_to_sequences([text])
            padded = pad_sequences(seq, maxlen=50)

            prediction = model.predict(padded, verbose=0)
            label = np.argmax(prediction)

            if label == 2:
                return "positive"
            elif label == 0:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            print("Prediction error:", e)

    # ---------- FALLBACK ----------
    return "neutral"