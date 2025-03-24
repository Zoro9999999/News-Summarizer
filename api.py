# api.py
import requests

def get_articles_api(company_name):
    try:
       
        api_key = "4a925976ff6041f8abf459a4241556ae"
        url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}&language=en&sortBy=publishedAt"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            return {"status": "error", "message": data.get("message", "Unknown error")}
        
        articles = []
        for article in data.get("articles", [])[:10]:  # Limit to 10 articles
            articles.append({
                "title": article.get("title", "No title"),
                "url": article.get("url", "No URL"),
                "raw_content": article.get("content", "No content") or "No content available",
                "processed_content": (article.get("content", "No content") or "No content available").lower()
            })
        return {"status": "success", "articles": articles}
    except Exception as e:
        return {"status": "error", "message": str(e)}