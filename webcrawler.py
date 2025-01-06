import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from queue import PriorityQueue

#modified code from the references in the assignement: https://www.scrapingbee.com/blog/crawling-python/

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, seed_urls=[], max_pages = 100, keywords = None):
        self.max_pages = max_pages
        self.keywords = keywords or []
        self.visited_urls = set()
        self.priority_queue = PriorityQueue()
        self.downloaded_pages = 0

        for url in seed_urls:
            self.priority_queue.put((-1, url))

    def is_relevant(self, text):
        if not self.keywords:
            return True
        return any(keyword.lower() in text.lower() for keyword in self.keywords)
    
    def calculate_score(self, text):
        if not self.keywords:
            return 0
        return sum(keyword.lower() in text.lower() for keyword in self.keywords) / len(self.keywords)

    def download_url(self, url):
        return requests.get(url, timeout=5).text
    
    def save_page(self, url, content):
        if requests.get(url).status_code == 200:
            file_name = str(self.downloaded_pages) + ".html"
            file = open(file_name, "w") 
            file.write(requests.get(url).text)
            file = open("List_of_URLS.txt", "a")
            file.write(url + "\n")
            print("HTML saved successfully!")
        else:
            print("Failed to retrieve the HTML.")

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            path = link.get('href')
            if path and path.startswith(('http', 'https')):
                yield path, link.text
            elif path and path.startswith('/'):
                yield urljoin(url, path), link.text

    def add_url_to_visit(self, url, anchor_text):
        if url not in self.visited_urls and url not in [item[1] for item in self.priority_queue.queue]:
            score = self.calculate_score(anchor_text)
            if score > 0:
                self.priority_queue.put((-score, url))

    def crawl(self, url):
        html = self.download_url(url)
        if self.is_relevant(html):
            self.save_page(url, html)
            self.downloaded_pages += 1
            for linked_url, anchor_text in self.get_linked_urls(url, html):
                self.add_url_to_visit(linked_url, anchor_text)

    def run(self):
        while not self.priority_queue.empty() and self.downloaded_pages < self.max_pages:
            _, url = self.priority_queue.get()
            if url not in self.visited_urls:
                logging.info(f'Crawling: {url}')
                try:
                    self.crawl(url)
                except Exception:
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    self.visited_urls.add(url)

if __name__ == '__main__':
    seed_urls = ['https://www.atlantanewsfirst.com/2024/09/18/standing-ovation-apalachee-high-school-marching-band-performs-first-time-since-deadly-shooting/'
                 , 'https://apnews.com/article/georgia-high-school-shooting-security-a4d04e85963e3a0cada2e2dd4d223e07'
                 , 'https://en.wikipedia.org/wiki/2024_Apalachee_High_School_shooting'
                 , 'https://www.local10.com/news/national/2024/09/17/after-shooting-at-georgia-high-school-students-will-return-next-week-for-half-days/'
                 , 'https://abcnews.go.com/US/teacher-shot-georgia-high-school-life-hands-amid/story?id=113736231']
    keywords = ['apalachee', 'high school', 'georgia', 'shooting', 'september']
    Crawler(seed_urls=seed_urls, max_pages=100, keywords=keywords).run()