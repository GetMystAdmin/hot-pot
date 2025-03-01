import requests
import json
from typing import Dict, List, Optional

class NewsAPI:
    def __init__(self):
        self.base_url = "https://saurav.tech/NewsAPI/top-headlines/category"
    
    def fetch_news(self, category: str) -> Optional[Dict]:
        """
        Fetch news from the specified category
        :param category: 'entertainment' or 'general'
        :return: JSON response with news articles
        """
        url = f"{self.base_url}/{category}/us.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {category} news: {e}")
            return None
    
    def get_articles(self, category: str, limit: int = 5) -> List[Dict]:
        """
        Get articles from a specific category
        :param category: 'entertainment' or 'general'
        :param limit: number of articles to return (default 5)
        :return: List of article dictionaries
        """
        news_data = self.fetch_news(category)
        if news_data:
            return news_data.get('articles', [])[:limit]
        return []

def display_news(articles: List[Dict], category: str):
    """
    Display formatted news articles
    :param articles: List of article dictionaries
    :param category: Category name for display purposes
    """
    if articles:
        print(f"\n{category.title()} News:")
        for idx, article in enumerate(articles, 1):
            print(f"\n{idx}. {article['title']}")
            print(f"Source: {article['source']['name']}")
            print(f"Description: {article['description']}")

def main():
    news_api = NewsAPI()
    
    # Fetch entertainment news
    entertainment_articles = news_api.get_articles('entertainment')
    display_news(entertainment_articles, 'entertainment')
    
    # Fetch general news
    general_articles = news_api.get_articles('general')
    display_news(general_articles, 'general')

if __name__ == "__main__":
    main()