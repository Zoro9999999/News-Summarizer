import streamlit as st
from utils import summarize_text, text_to_speech_hindi, text_to_speech_hindi_limited
from model import analyze_sentiment
from api import get_articles_api

def get_emoji_sentiment(sentiment):
    if sentiment == "Positive":
        return "😊"
    elif sentiment == "Negative":
        return "😞"
    return "😐"

def comparative_analysis(articles):
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for article in articles:
        sentiment_dist[article['Sentiment']] += 1
    
    total = sum(sentiment_dist.values())
    if total == 0:
        return "Neutral", 0.0, "No articles to analyze."
    
    score = (sentiment_dist["Positive"] * 100 + sentiment_dist["Neutral"] * 50) / total
    if sentiment_dist["Positive"] > sentiment_dist["Negative"] and sentiment_dist["Positive"] >= sentiment_dist["Neutral"]:
        overall_sentiment = "Positive"
    elif sentiment_dist["Negative"] > sentiment_dist["Positive"] and sentiment_dist["Negative"] >= sentiment_dist["Neutral"]:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"
    
    summary = f"प्रस्तुत लेखों में से {sentiment_dist['Positive']} सकारात्मक, {sentiment_dist['Negative']} नकारात्मक, और {sentiment_dist['Neutral']} तटस्थ हैं। कुल मिलाकर भावना {overall_sentiment.lower()} है।"
    return overall_sentiment, score, summary

def main():
    st.title("News Summarization and Sentiment Analyzer")
    st.write("Enter a company name to analyze news articles.")
    
    company_name = st.text_input("Company Name", "")
    
    if st.button("Analyze News"):
        if not company_name.strip():
            st.error("Please enter a company name.")
            return
        
        spinner = st.spinner(f"Fetching articles for {company_name}...")
        with spinner:
            try:
                response = get_articles_api(company_name)
                if response.get("status") == "error":
                    st.error(f"Error fetching articles: {response.get('message', 'Unknown error')}")
                    return
                articles = response.get("articles", [])
            except Exception as e:
                st.error(f"Error fetching articles: {str(e)}")
                return
        
        if articles:
            st.success(f"Found {len(articles)} articles!")
            processed_articles = []
            
            for i, article in enumerate(articles, 1):
                try:
                    content = article.get('processed_content', article.get('content', ''))
                    sentiment, score = analyze_sentiment(content or "No content available")
                    summary = summarize_text(content or "No content available")
                    
                    st.header(f"Article {i}: {article.get('title', 'Untitled')}")
                    
                    with st.expander("View URL and Full Content"):
                        st.write(f"**URL**: {article.get('url', 'No URL')}")
                        st.write(f"**Full Content**: {article.get('raw_content', content)}")
                    
                    st.subheader("Summary (4-5 sentences)")
                    st.text_area(f"Summary of Article {i}", summary, height=150, key=f"summary_{i}")
                    
                    st.subheader("Sentiment Analysis")
                    st.write(f"Sentiment: {sentiment} ({score:.2f})")
                    sentiment_value = {"Positive": 100, "Neutral": 50, "Negative": 0}.get(sentiment, 50)
                    st.slider(
                        f"Sentiment for Article {i}",
                        min_value=0,
                        max_value=100,
                        value=sentiment_value,
                        format=f"{get_emoji_sentiment(sentiment)} %d",
                        disabled=True,
                        key=f"sentiment_{i}"
                    )
                    st.subheader("Hindi Audio Summary")
                    audio_file = text_to_speech_hindi_limited(summary, i)
                    st.audio(audio_file, format="audio/mp3")
                    
                    processed_articles.append({"Sentiment": sentiment})
                    
                    st.markdown("---")
                except Exception as e:
                    st.warning(f"Error processing article {i}: {str(e)}")
                    continue
            
            st.header("Comparative Analysis of All Articles")
            overall_sentiment, overall_score, hindi_summary = comparative_analysis(processed_articles)
            
            st.write(f"Overall Sentiment: {overall_sentiment}")
            st.slider(
                "Overall Sentiment Across Articles",
                min_value=0,
                max_value=100,
                value=int(overall_score),
                format=f"{get_emoji_sentiment(overall_sentiment)} %d",
                disabled=True,
                key="overall_sentiment"
            )
            
            st.subheader("Comparative Sentiment Audio (Hindi)")
            comparative_audio_file = text_to_speech_hindi(hindi_summary)
            st.audio(comparative_audio_file, format="audio/mp3")

        else:
            st.error("No articles found or an error occurred.")

if __name__ == "__main__":
    main()