from transformers import pipeline
import pandas as pd

def perform_sentiment_analysis(review_file, output_file="data/sentiment_analysis.csv"):
    reviews = pd.read_csv(review_file)

    sentiment_analyzer = pipeline("sentiment-analysis")
    reviews["sentiment"] = reviews["content"].apply(lambda x: sentiment_analyzer(x)[0]['label'] if pd.notna(x) else None)

    reviews.to_csv(output_file, index=False)
    print(f"Sentiment analysis results saved to {output_file}")

# ========================= FILE: storage/database_manager.py =========================
from sqlalchemy import create_engine
import pandas as pd

def save_to_database(json_file, db_url="sqlite:///data/market_research.db", table_name="competitor_data"):
    engine = create_engine(db_url)

    data = pd.read_json(json_file)
    data.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"Data saved to database in table: {table_name}")
