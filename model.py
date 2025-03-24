import nltk
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "sentiment", "vader_lexicon")):
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(text):
    """Perform sentiment analysis using VADER."""
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    if scores['compound'] >= 0.05:
        return 'Positive', scores['compound']
    elif scores['compound'] <= -0.05:
        return 'Negative', scores['compound']
    else:
        return 'Neutral', scores['compound']