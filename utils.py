import nltk
import os
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from transformers import pipeline
from gtts import gTTS
from deep_translator import GoogleTranslator

# Ensure NLTK downloads
nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
    nltk.download('punkt', quiet=True)
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt_tab")):
    nltk.download('punkt_tab', quiet=True)

def scrape_articles(company_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    articles = []
   
    search_query = f'"{company_name}" news "about {company_name}" -inurl:(signup login forum blog directory)'
    
    try:
        search_results = list(search(search_query, num_results=200))
        if not search_results:
            print(f"No search results found for {company_name}")
            return articles
        
        processed_urls = set()
        for url in search_results:
            if len(articles) >= 10:
                break
            if url in processed_urls:
                print(f"Skipping duplicate URL: {url}")
                continue
            try:
                time.sleep(2)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = soup.title.string if soup.title else "No title found"
                paragraphs = soup.find_all('p')
                raw_content = ' '.join([p.get_text().strip() for p in paragraphs])
                if not raw_content or len(raw_content.split()) < 20:
                    print(f"Skipping '{title}' - insufficient content (word count: {len(raw_content.split())})")
                    continue
                
                company_name_lower = company_name.lower()
                title_lower = title.lower()
                content_lower = raw_content.lower()
                company_mention_count = content_lower.count(company_name_lower)
                
                if not (company_name_lower in title_lower or company_mention_count >= 1):
                    print(f"Skipping article '{title}' - not relevant to {company_name} (mentions: {company_mention_count})")
                    continue
                
                summary = summarize_text(raw_content)
                articles.append({
                    'title': title,
                    'url': url,
                    'raw_content': raw_content,
                    'summary': summary,
                    'processed_content': raw_content.lower()
                })
                processed_urls.add(url)
                print(f"Added article '{title}' - relevant to {company_name} (mentions: {company_mention_count}, word count: {len(raw_content.split())})")
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
        
        if len(articles) < 10:
            print(f"Initial search found only {len(articles)} articles. Performing broader search...")
            fallback_query = f'"{company_name}" news'
            fallback_results = list(search(fallback_query, num_results=100))
            for url in fallback_results:
                if len(articles) >= 10:
                    break
                if url in processed_urls:
                    print(f"Skipping duplicate URL: {url}")
                    continue
                try:
                    time.sleep(2)
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title = soup.title.string if soup.title else "No title found"
                    paragraphs = soup.find_all('p')
                    raw_content = ' '.join([p.get_text().strip() for p in paragraphs])
                    if not raw_content or len(raw_content.split()) < 20:
                        print(f"Skipping '{title}' - insufficient content (word count: {len(raw_content.split())})")
                        continue
                    
                    company_name_lower = company_name.lower()
                    title_lower = title.lower()
                    content_lower = raw_content.lower()
                    company_mention_count = content_lower.count(company_name_lower)
                    
                    if not (company_name_lower in title_lower or company_mention_count >= 2):
                        print(f"Skipping article '{title}' - not relevant to {company_name} (mentions: {company_mention_count})")
                        continue
                    
                    summary = summarize_text(raw_content)
                    articles.append({
                        'title': title,
                        'url': url,
                        'raw_content': raw_content,
                        'summary': summary,
                        'processed_content': raw_content.lower()
                    })
                    processed_urls.add(url)
                    print(f"Added article '{title}' - relevant to {company_name} (mentions: {company_mention_count}, word count: {len(raw_content.split())})")
                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
                    continue
        
        if len(articles) < 10:
            print(f"Warning: Only {len(articles)} relevant articles found for {company_name} after exhaustive search.")
        else:
            print(f"Success: Found {len(articles)} relevant articles for {company_name}.")
        return articles
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return articles

def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    max_length = 120
    min_length = 80
    summary = summarizer(text[:4000], max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def text_to_speech_hindi(text):
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = text
    
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = "summary.mp3"
    tts.save(audio_file)
    time.sleep(2)
    return audio_file

def text_to_speech_hindi_limited(text, index):
    words = text.split()
    target_words = min(len(words), 120)
    limited_text = " ".join(words[:target_words])
    
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(limited_text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = limited_text
    
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = f"summary_{index}.mp3"
    tts.save(audio_file)
    time.sleep(2)
    return audio_file