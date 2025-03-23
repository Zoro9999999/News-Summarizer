from utils import scrape_articles

def get_articles_api(company_name):
    try:
        articles = scrape_articles(company_name)
        return {"status": "success", "articles": articles}
    except Exception as e:
        return {"status": "error", "message": str(e)}