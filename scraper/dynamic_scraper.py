from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_dynamic_reviews(output_file="data/reviews.csv"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.example-review-site.com/product-reviews")

        # Handle infinite scroll to load more reviews
        for _ in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

        # Extract review content
        reviews = []
        for review in page.query_selector_all('.review-item'):
            reviews.append({
                'username': review.query_selector('.username').inner_text() if review.query_selector('.username') else None,
                'rating': review.query_selector('.rating').inner_text() if review.query_selector('.rating') else None,
                'content': review.query_selector('.review-text').inner_text() if review.query_selector('.review-text') else None
            })

        browser.close()

        df = pd.DataFrame(reviews)
        df.to_csv(output_file, index=False)
        print(f"Reviews saved to {output_file}")
