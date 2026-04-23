import pandas as pd
import numpy as np
import re
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# 1. Load Data
df = pd.read_csv("sentimentdataset.csv")

# 2. Map Granular Emotions to Root Sentiment Classes
positive_emotions = ["Positive", "Happiness", "Joy", "Love", "Amusement", "Enjoyment", "Admiration", "Affection", "Awe", "Surprise", "Acceptance", "Adoration", "Anticipation", "Calmness", "Excitement", "Kind", "Pride", "Hope", "Empowerment", "Compassion", "Tenderness", "Arousal", "Enthusiasm", "Fulfillment", "Reverence", "Elation", "Euphoria", "Contentment", "Serenity", "Gratitude", "Curiosity", "Thrill", "Overjoyed", "Inspiration", "Motivation", "Blessed", "Reflection", "Appreciation", "Confidence", "Accomplishment", "Wonderment", "Optimism", "Enchantment", "Intrigue", "PlayfulJoy", "Mindfulness", "DreamChaser", "Elegance", "Whimsy", "Pensive", "Harmony", "Creativity", "Radiance", "Wonder", "Rejuvenation", "Coziness", "CulinaryOdyssey", "Resilience", "Immersion", "Spark", "Marvel", "Zest", "Hopeful", "Proud", "Grateful", "Empathetic", "Compassionate", "Playful", "Free-spirited", "Inspired", "Confident", "Radiance", "Thrill", "Reflection", "Exploration", "Romance", "Captivation", "Wonder", "Tranquility", "Grandeur", "Emotion", "Energy", "Celebration", "Charm", "Ecstasy", "Anticipation", "Engagement", "Touched", "Suspense", "Satisfaction", "Triumph", "Fascination"]

# Some emotions exist with trailing spaces in CSV, strip them first
df['Sentiment'] = df['Sentiment'].str.strip()

# Create a mapping function
def map_sentiment(emotion):
    if emotion in positive_emotions:
        return 2  # Positive
    elif emotion in ["Neutral", "Indifference", "Curiosity", "Nostalgia", "Ambivalence", "Contemplation"]:
        return 1  # Neutral
    else:
        # Default anything else (Anger, Sadness, Disappointed, Bitter, Fear, Disgust, Heartache, etc.) to 0 (Negative)
        return 0  # Negative

df['Label'] = df['Sentiment'].apply(map_sentiment)

# 3. Clean Text
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

df['Clean_Text'] = df['Text'].apply(clean_text)

# 4. Tokenization (Limiting words for speed)
MAX_WORDS = 5000
MAX_EPOCHS = 5
MAX_LEN = 50 # pad to 50 words

tokenizer = Tokenizer(num_words=MAX_WORDS)
tokenizer.fit_on_texts(df['Clean_Text'])
sequences = tokenizer.texts_to_sequences(df['Clean_Text'])
X = pad_sequences(sequences, maxlen=MAX_LEN)

# One-hot encode labels
y = to_categorical(df['Label'], num_classes=3)

# 5. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Build Deep Learning LSTM Architecture
model = Sequential()
model.add(Embedding(input_dim=MAX_WORDS, output_dim=64, input_length=MAX_LEN))
model.add(LSTM(64, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 7. Train the Artificial Intelligence
print("Beginning AI Training Protocol...")
model.fit(X_train, y_train, epochs=MAX_EPOCHS, batch_size=32, validation_data=(X_test, y_test))

# 8. Save Weights and Tokenizer
model.save("sentiment_dl_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("Training Complete! The AI 'sentiment_dl_model.h5' and 'tokenizer.pkl' have been saved successfully.")
