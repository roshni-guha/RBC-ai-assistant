"""
News Fetcher
Uses NewsAPI to fetch financial news for stocks
"""

from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class NewsFetcher:
    """Fetch financial news using NewsAPI"""

    def __init__(self, apiKey: str):
        """
        Initialize NewsAPI client

        Args:
            apiKey: Your NewsAPI key (get free key at https://newsapi.org/)
        """
        self.newsapi = NewsApiClient(api_key=apiKey)
        self.apiKey = apiKey

    def getStockNews(self, ticker: str, companyName: str = None, numArticles: int = 10) -> List[Dict]:
        """
        Get news articles for a specific stock

        Args:
            ticker: Stock ticker symbol
            companyName: Optional company name for better search results
            numArticles: Number of articles to fetch (default: 10)

        Returns:
            List of news articles
        """
        # Build search query
        if companyName:
            query = f'"{ticker}" OR "{companyName}"'
        else:
            query = ticker

        # Get news from last 7 days
        sevenDaysAgo = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        try:
            # Search for everything mentioning the stock
            allArticles = self.newsapi.get_everything(
                q=query,
                from_param=sevenDaysAgo,
                language='en',
                sort_by='publishedAt',
                page_size=numArticles
            )

            if allArticles['status'] == 'ok':
                articles = allArticles['articles']

                # Format articles
                formattedArticles = []
                for article in articles:
                    formattedArticles.append({
                        'title': article.get('title', 'N/A'),
                        'description': article.get('description', 'N/A'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'publishedAt': article.get('publishedAt', 'N/A'),
                        'url': article.get('url', '#')
                    })

                return formattedArticles
            else:
                return []

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def getTopFinancialNews(self, numArticles: int = 10) -> List[Dict]:
        """
        Get top financial news headlines

        Args:
            numArticles: Number of articles to fetch

        Returns:
            List of top financial news articles
        """
        try:
            # Get top business headlines
            topHeadlines = self.newsapi.get_top_headlines(
                category='business',
                language='en',
                country='us',
                page_size=numArticles
            )

            if topHeadlines['status'] == 'ok':
                articles = topHeadlines['articles']

                formattedArticles = []
                for article in articles:
                    formattedArticles.append({
                        'title': article.get('title', 'N/A'),
                        'description': article.get('description', 'N/A'),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'publishedAt': article.get('publishedAt', 'N/A'),
                        'url': article.get('url', '#')
                    })

                return formattedArticles
            else:
                return []

        except Exception as e:
            print(f"Error fetching top news: {e}")
            return []

    def printStockNews(self, ticker: str, companyName: str = None):
        """Print formatted news for a stock"""
        print(f"\n{'='*80}")
        print(f"FINANCIAL NEWS: {ticker}")
        if companyName:
            print(f"Company: {companyName}")
        print(f"{'='*80}\n")

        articles = self.getStockNews(ticker, companyName)

        if not articles:
            print("No news articles found.")
            return

        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']} | {article['publishedAt'][:10]}")
            if article['description'] != 'N/A':
                print(f"   {article['description'][:150]}...")
            print(f"   URL: {article['url']}")
            print()

        print(f"{'='*80}\n")


def main():
    """Test the news fetcher"""
    # NOTE: You need to get your own API key from https://newsapi.org/
    # Free tier allows 100 requests per day

    apiKey = input("Enter your NewsAPI key: ").strip()

    if not apiKey:
        print("No API key provided. Get one free at https://newsapi.org/")
        return

    ticker = input("Enter ticker symbol: ").strip().upper()
    companyName = input("Enter company name (optional): ").strip()

    if not ticker:
        print("No ticker provided.")
        return

    fetcher = NewsFetcher(apiKey)
    fetcher.printStockNews(ticker, companyName if companyName else None)


if __name__ == "__main__":
    main()
