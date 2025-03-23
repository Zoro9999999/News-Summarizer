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
        # Reduced num_results from 50 to 20 to speed up the search
        search_results = search(search_query, num_results=20)
        for url in search_results:
            if len(articles) >= 10:
                break
            try:
                # Reduced delay from 5 seconds to 1 second
                time.sleep(1)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = soup.title.string if soup.title else "No title found"
                paragraphs = soup.find_all('p')
                raw_content = ' '.join([p.get_text().strip() for p in paragraphs])
                if not raw_content:
                    continue
                
                # Relevance check: Ensure the company name appears in the title or frequently in the content
                company_name_lower = company_name.lower()
                title_lower = title.lower()
                content_lower = raw_content.lower()
                company_mention_count = content_lower.count(company_name_lower)
                
                # Require the company name in the title OR at least 3 mentions in the content
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
    # Translate English text to Hindi
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = text  # Fallback to original text if translation fails
    
    # Generate audio in Hindi
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = "summary.mp3"
    tts.save(audio_file)
    return audio_file

def text_to_speech_hindi_limited(text, index):
    # Limit to ~3-4 minutes (180-240 seconds)
    # gTTS normal speed is ~200 words/minute, so ~600-800 words for 3-4 mins
    words = text.split()
    target_words = min(len(words), 700)  # Aim for ~3.5 minutes (700 words)
    limited_text = " ".join(words[:target_words])
    
    # Translate English text to Hindi
    try:
        translated_text = GoogleTranslator(source='en', target='hi').translate(limited_text)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        translated_text = limited_text  # Fallback to original text if translation fails
    
    # Generate audio in Hindi
    tts = gTTS(text=translated_text, lang='hi', slow=False)
    audio_file = f"summary_{index}.mp3"
    tts.save(audio_file)
    return audio_file