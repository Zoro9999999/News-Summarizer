import requests

def get_articles_api(company_name):
    try:
        api_key = "4a925976ff6041f8abf459a4241556ae"
        url = f"https://newsapi.org/v2/everything?q=\"{company_name}\" news&apiKey={api_key}&language=en&sortBy=relevancy&pageSize=100"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "ok":
            return {"status": "error", "message": data.get("message", "Unknown error")}

        articles = []
        company_name_lower = company_name.lower()
        for article in data.get("articles", []):
            title = article.get("title", "No title").lower()
            raw_content = article.get("content", "No content") or "No content available"
            content_lower = raw_content.lower()
            word_count = len(raw_content.split())
            
            if word_count < 20:
                continue
            
            company_mention_count = content_lower.count(company_name_lower)
            if not (company_name_lower in title or company_mention_count >= 3):
                continue
            
            articles.append({
                "title": article.get("title", "No title"),
                "url": article.get("url", "No URL"),
                "raw_content": raw_content,
                "processed_content": content_lower
            })
            
            if len(articles) >= 10:
                break
        
        if len(articles) < 10:
            return {"status": "error", "message": f"Found only {len(articles)} relevant articles for {company_name}. Need exactly 10."}
        
        return {"status": "success", "articles": articles}
    except Exception as e:
        return {"status": "error", "message": str(e)}