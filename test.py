from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import emoji
from deep_translator import GoogleTranslator

analyzer = SentimentIntensityAnalyzer()
emojis = ["🤮", "🔥", "😡", "💔", "😍"]

for e in emojis:
    dem = emoji.demojize(e, delimiters=(" ", " "))
    print(f"Demojized: {dem}")
    dem_no_undescore = dem.replace("_", " ")
    print(f"No underscore: {dem_no_undescore}")
    print(f"VADER on demojized: {analyzer.polarity_scores(dem)}")
    print(f"VADER on no underscore: {analyzer.polarity_scores(dem_no_undescore)}")
    print("-" * 30)
