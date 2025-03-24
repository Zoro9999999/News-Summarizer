import nltk
import os

nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
    nltk.download('punkt', quiet=True)
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt_tab")):
    nltk.download('punkt_tab', quiet=True)

import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from gtts import gTTS
from deep_translator import GoogleTranslator

def scrape_articles(company_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    articles = []
    search_query = f'"{company_name}" "news" "about {company_name}" site:*.edu | site:*.org | site:*.gov -inurl:(signup | login)'
    
    try:
        search_results = search(search_query, num_results=20)
        for url in search_results:
            if len(articles) >= 10:
                break
            try:
                time.sleep(2)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = soup.title.string if soup.title else "No title found"
                paragraphs = soup.find_all('p')
                raw_content = ' '.join([p.get_text().strip() for p in paragraphs])
                if not raw_content:
                    continue
                
                
                company_name_lower = company_name.lower()
                title_lower = title.lower()
                content_lower = raw_content.lower()
                company_mention_count = content_lower.count(company_name_lower)
                
                if not (company_name_lower in title_lower or company_mention_count >= 3):
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
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
        return articles
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return articles

def summarize_text(text, sentence_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return ' '.join([str(sentence) for sentence in summary])

def summarize_text_500_words(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 25)
    summary_text = ' '.join([str(sentence) for sentence in summary])
    while len(summary_text.split()) < 450:
        summary_text += " " + text[:2500]
    return ' '.join(summary_text.split()[:500])

def text_to_speech_hindi(text):
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = text  
    
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = "summary.mp3"
    tts.save(audio_file)
    return audio_file

def text_to_speech_hindi_limited(text, index):
    words = text.split()
    target_words = min(len(words), 700) 
    limited_text = " ".join(words[:target_words])
    
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(limited_text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = limited_text  
   
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = f"summary_{index}.mp3"
    tts.save(audio_file)
    return audio_file