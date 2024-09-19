#!/usr/bin/env python3
import requests
import re
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import random
import argparse
import sys

"""
pip install
beautifulsoup4
requests
"""

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
]

class Scanner:
    def __init__(self, url, ignore_links=None):
        self.session = requests.Session()
        self.set_random_user_agent()
        self.target_url = url.rstrip('/')
        self.target_links = set()
        self.ignore_links = set(ignore_links) if ignore_links else set()
        self.forms = []
        self.comments = []
        self.versions = []
        self.max_depth = 3  # Limit the crawling depth to prevent infinite loops

    def set_random_user_agent(self):
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

    def extract_links(self, url):
        try:
            response = self.session.get(url)
            # Collect comments
            self.extract_comments(response.text, url)
            # Collect version info
            self.extract_versions(response.text, response.headers, url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urlparse.urljoin(url, href)
                if self.target_url in full_url and full_url not in self.ignore_links:
                    links.add(full_url.split('#')[0])
            return links
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
            return set()

    def extract_forms(self, url):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            forms = soup.find_all('form')
            for form in forms:
                self.forms.append({'url': url, 'form': form})
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")

    def extract_comments(self, html_content, url):
        comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
        for comment in comments:
            self.comments.append({'url': url, 'comment': comment.strip()})

    def extract_versions(self, html_content, headers, url):
        # Check for version info in meta tags
        soup = BeautifulSoup(html_content, 'html.parser')
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            self.versions.append({'url': url, 'version': generator['content']})

        # Check for version info in headers
        server_header = headers.get('Server')
        if server_header:
            self.versions.append({'url': url, 'version': server_header})

    def crawl(self, url, depth=0):
        if depth > self.max_depth:
            return
        links = self.extract_links(url)
        for link in links:
            if link not in self.target_links:
                self.target_links.add(link)
                print(f"Discovered URL: {link}")
                self.extract_forms(link)
                self.crawl(link, depth + 1)

    def run(self):
        print(f"Starting crawl on {self.target_url}")
        self.crawl(self.target_url)
        print("\nCrawl completed.")
        self.print_report()

    def print_report(self):
        print("\n--- Crawl Report ---")
        print(f"Total unique URLs discovered: {len(self.target_links)}")
        print("\nForms discovered:")
        for form_info in self.forms:
            print(f"URL: {form_info['url']}")
            print(f"Form: {form_info['form']}\n")

        print("Comments found in HTML:")
        for comment_info in self.comments:
            print(f"URL: {comment_info['url']}")
            print(f"Comment: {comment_info['comment']}\n")

        print("Version information discovered:")
        for version_info in self.versions:
            print(f"URL: {version_info['url']}")
            print(f"Version: {version_info['version']}\n")

def main():
    parser = argparse.ArgumentParser(description="Simple Web Application Spider")
    parser.add_argument("url", help="Target URL to scan")
    parser.add_argument("-i", "--ignore", nargs='*', default=[], help="List of URLs to ignore")
    args = parser.parse_args()

    target_url = args.url
    ignore_links = args.ignore

    scanner = Scanner(target_url, ignore_links)
    scanner.run()

if __name__ == "__main__":
    main()



"""
./ctf-spider.py "http://10.10.10.10"

You can also specify URLs to ignore:
./ctf-spider.py "http://10.10.10.10" -i "http://10.10.10.10/logout"


Starting crawl on http://10.10.234.18
Discovered URL: http://10.10.234.18/admissions.html
Discovered URL: http://10.10.234.18/index.html
Discovered URL: http://10.10.234.18/contact.html
Discovered URL: http://10.10.234.18/courses.html
Discovered URL: http://10.10.234.18/about.html
Discovered URL: http://10.10.234.18

Crawl completed.

--- Crawl Report ---
Total unique URLs discovered: 6

Forms discovered:
URL: http://10.10.234.18/contact.html
Form: <form action="#" method="POST">
<label for="name">Name:</label>
<input id="name" name="name" required="" type="text"/>
<label for="email">Email:</label>
<input id="email" name="email" required="" type="email"/>
<label for="subject">Subject:</label>
<input id="subject" name="subject" required="" type="text"/>
<label for="message">Message:</label>
<textarea id="message" name="message" required="" rows="5"></textarea>
<input type="submit" value="Submit"/>
</form>

Comments found in HTML:
Version information discovered:
URL: http://10.10.234.18
Version: Apache/2.4.41 (Ubuntu)

URL: http://10.10.234.18/admissions.html
Version: Apache/2.4.41 (Ubuntu)

URL: http://10.10.234.18/index.html
Version: Apache/2.4.41 (Ubuntu)

URL: http://10.10.234.18/contact.html
Version: Apache/2.4.41 (Ubuntu)

URL: http://10.10.234.18
Version: Apache/2.4.41 (Ubuntu)
"""