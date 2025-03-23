from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

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