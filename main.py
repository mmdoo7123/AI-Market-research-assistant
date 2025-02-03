from scraper.dynamic_scraper import scrape_dynamic_reviews
from analysis.sentiment_analysis import perform_sentiment_analysis
from storage.database_manager import save_to_database

if __name__ == "__main__":
    # Step 1: Run the Scrapy spider separately: scrapy runspider spiders/competitor_spider.py

    # Step 2: Scrape Dynamic Reviews
    scrape_dynamic_reviews()

    # Step 3: Perform Sentiment Analysis
    perform_sentiment_analysis("data/reviews.csv")

    # Step 4: Save Competitor Data to Database
    save_to_database("data/competitor_data.json")

    print("All processes complete! Dashboard can now be launched.")
