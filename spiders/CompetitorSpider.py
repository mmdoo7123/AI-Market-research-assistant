import scrapy
import json
import random
import requests
from bs4 import BeautifulSoup


class CompetitorSpider(scrapy.Spider):
    name = "dynamic_proxy_spider"

    def __init__(self, site_name, query, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("site_config.json", "r") as f:
            self.site_config = json.load(f)[site_name]
        self.start_urls = [self.site_config["base_url"].format(query=query)]
        self.seen_urls = set()

        # Dynamically fetch proxy list
        self.proxies = self.fetch_proxies()

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_TIMEOUT': 10,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.google.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    },
    }
    def validate_proxy(proxy):
        """Check if a proxy is valid by making a test request."""
        try:
            test_url = "https://www.amazon.com"
            proxies = {"https": f"http://{proxy}"}
            response = requests.get(test_url, proxies=proxies, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    def start_requests(self):
        """Send requests using proxies, with fallback on failure."""
        for url in self.start_urls:
            for _ in range(len(self.proxies)):
                proxy = self.get_random_proxy()
                if proxy:
                    self.logger.info(f"Using proxy: {proxy} for {url}")
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        errback=self.handle_error,
                        meta={'proxy': f'http://{proxy}'},
                    )
                else:
                    self.logger.warning("No working proxies available! Skipping request.")
                    break

    def handle_error(self, failure):
        """Handle failed requests and retry with another proxy."""
        self.logger.error(f"Request failed: {failure.value}")
        request = failure.request
        proxy = self.get_random_proxy()
        if proxy:
            self.logger.info(f"Retrying {request.url} with new proxy: {proxy}")
            request.meta['proxy'] = f"http://{proxy}"
            yield request
        else:
            self.logger.error("No working proxies left. Giving up.")

    def fetch_proxies(self):
        proxies = []
        try:
            response = requests.get("https://free-proxy-list.net/")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Locate the proxy table using the structure you provided
                table = soup.find("table", {"id": "proxylisttable"})
                if table:
                    rows = table.find("tbody").find_all("tr")
                    for row in rows:
                        cols = row.find_all("td")
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        https = cols[6].text.strip().lower() == "yes"
                        if https:  # Only include HTTPS proxies
                            proxy = f"{ip}:{port}"
                            if self.validate_proxy(proxy):
                                proxies.append(proxy)
                    self.logger.info(f"Fetched {len(proxies)} proxies.")
                else:
                    self.logger.error("Proxy table not found on the page.")
            else:
                self.logger.error(f"Failed to fetch the page: HTTP {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to fetch proxies: {e}")
        return proxies

    def get_random_proxy(self):
        """Get a random proxy from the dynamically fetched list."""
        if not self.proxies:
            if not hasattr(self, "_logged_proxy_warning"):  # Log once
                self.logger.warning("No proxies available! Using direct connection.")
                self._logged_proxy_warning = True
            return None
        return random.choice(self.proxies)

    def start_requests(self):
        """Send requests using a random proxy for each URL."""
        for url in self.start_urls:
            proxy = self.get_random_proxy()
            if proxy:
                self.logger.info(f"Using proxy: {proxy} for {url}")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'proxy': f'http://{proxy}'},
                )
            else:
                self.logger.warning("Proceeding without proxy.")
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse the response and extract product data."""
        if response.status != 200:
            self.logger.error(f"Failed to retrieve page: {response.url}")
            return

        selectors = self.site_config["selectors"]
        products = response.css(selectors["product"])
        self.logger.info(f"Scraped {len(products)} products from {response.url}")

        for product in products:
            name = product.css(selectors["name"]).get()
            price = product.css(selectors["price"]).get()
            rating = product.css(selectors["rating"]).get()
            url = response.urljoin(product.css(selectors["url"]).get())

            if name and price:
                yield {
                    'name': name.strip(),
                    'price': price.replace("$", "").strip() if price else "N/A",
                    'rating': rating.strip() if rating else "No rating",
                    'url': url,
                }

        next_page = response.css(self.site_config["pagination"]).get()
        if next_page:
            proxy = self.get_random_proxy()
            if proxy:
                self.logger.info(f"Following pagination to: {next_page} using proxy: {proxy}")
                yield response.follow(
                    next_page,
                    self.parse,
                    meta={'proxy': f'http://{proxy}'},
                )
            else:
                self.logger.warning("Proceeding with pagination without proxy.")
                yield response.follow(next_page, self.parse)
        else:
            self.logger.info("No more pages to scrape.")


# Test `fetch_proxies` outside the class:
if __name__ == "__main__":
    spider = CompetitorSpider("amazon", "smartphones")
    proxies = spider.fetch_proxies()
    print(f"Fetched {len(proxies)} proxies:")
    for proxy in proxies[:10]:  # Display first 10 proxies
        print(proxy)