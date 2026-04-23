import pickle
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

model = load_model("sentiment_dl_model.h5")

with open("tokenizer.pkl","rb") as f:
    tokenizer = pickle.load(f)

positive_words = [
    "good","great","amazing","love","awesome","nice","best","happy"
]

negative_words = [
    "bad","worst","terrible","hate","awful","ugly","stupid","trash"
]

def clean_text(text):

    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    return text


def predict_sentiment(text):

    text = clean_text(text)

    # keyword override (very useful for small datasets)
    for word in negative_words:
        if word in text:
            return "negative"

    for word in positive_words:
        if word in text:
            return "positive"

    seq = tokenizer.texts_to_sequences([text])

    padded = pad_sequences(seq, maxlen=50)

    prediction = model.predict(padded)

    label = prediction.argmax()

    if label == 2:
        return "positive"

    elif label == 0:
        return "negative"

    else:
        return "neutral"