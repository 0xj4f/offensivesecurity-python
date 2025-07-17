#!/usr/bin/env python3
import requests
import re
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import random
import argparse
import sys
import json
import os

# List of User-Agent strings to randomize requests
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
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
        self.results = {
            'target_url': self.target_url,
            'discovered_urls': [],
            'forms': [],
            'comments': [],
            'versions': []
        }

    def set_random_user_agent(self):
        """Set a random User-Agent for the session."""
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

    def extract_links(self, url):
        """
        Extract all unique links from a given URL.
        Also extracts comments and version information.
        """
        try:
            response = self.session.get(url, timeout=10)
            # Collect comments
            self.extract_comments(response.text, url)
            # Collect version info
            self.extract_versions(response.text, response.headers, url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urlparse.urljoin(url, href)
                # Remove URL fragments
                full_url = full_url.split('#')[0]
                # Normalize the URL
                parsed_full_url = urlparse.urlparse(full_url)
                normalized_url = parsed_full_url.scheme + "://" + parsed_full_url.netloc + parsed_full_url.path
                if self.target_url in normalized_url and normalized_url not in self.ignore_links:
                    links.add(normalized_url)
            return links
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")
            return set()

    def extract_forms(self, url):
        """
        Extract all forms from a given URL and store their HTML.
        """
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            forms = soup.find_all('form')
            for form in forms:
                form_details = {
                    'url': url,
                    'form_html': str(form)
                }
                self.forms.append(form_details)
                self.results['forms'].append(form_details)
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")

    def extract_comments(self, html_content, url):
        """
        Extract HTML comments from the content.
        """
        comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
        for comment in comments:
            comment_details = {'url': url, 'comment': comment.strip()}
            self.comments.append(comment_details)
            self.results['comments'].append(comment_details)

    def extract_versions(self, html_content, headers, url):
        """
        Extract version information using regex for SemVer and CalVer across the entire HTML.
        Capture the entire line where the version is found.
        Exclude lines containing certain keywords to avoid irrelevant captures.
        """
        # Regex patterns for SemVer and CalVer
        semver_pattern = r'\b\d+\.\d+\.\d+\b'
        calver_pattern = r'\b\d{4}\.\d{1,2}(?:\.\d{1,2})?\b'

        # Initialize a set to avoid duplicates
        versions_found = set()

        # Split the HTML content into lines for line-by-line processing
        lines = html_content.split('\n')

        for line in lines:
            # Skip lines that are likely to contain irrelevant version-like patterns
            exclusion_keywords = ['viewport', 'charset', 'description', 'keywords', 'content-type', 'initial-scale']
            if any(keyword in line.lower() for keyword in exclusion_keywords):
                continue
            # Search for SemVer
            semver_matches = re.findall(semver_pattern, line)
            # Search for CalVer
            calver_matches = re.findall(calver_pattern, line)
            # Combine matches
            for match in semver_matches + calver_matches:
                # Capture the entire line where the version was found
                version_info = {'url': url, 'version': match, 'line': line.strip()}
                versions_found.add(json.dumps(version_info))  # Use JSON string to make it hashable

        # Check Server header first and prioritize it
        server_header = headers.get('Server')
        if server_header:
            version_info = {'url': url, 'version': server_header, 'source': 'Server Header'}
            version_json = json.dumps(version_info)
            if version_json not in versions_found:
                self.versions.append(version_info)
                self.results['versions'].append(version_info)

        # Add found versions from HTML
        for version_json in versions_found:
            version_info = json.loads(version_json)
            # Avoid duplicates
            if version_info not in self.versions:
                self.versions.append(version_info)
                self.results['versions'].append(version_info)

    def crawl(self, url, depth=0):
        """
        Recursively crawl the website to discover all unique URLs up to max_depth.
        """
        if depth > self.max_depth:
            return
        links = self.extract_links(url)
        for link in links:
            if link not in self.target_links:
                self.target_links.add(link)
                self.results['discovered_urls'].append(link)
                print(f"Discovered URL: {link}")
                self.extract_forms(link)
                self.crawl(link, depth + 1)

    def run(self):
        """
        Start the crawling process and generate reports.
        """
        print(f"Starting crawl on {self.target_url}")
        self.crawl(self.target_url)
        print("\nCrawl completed.")
        self.print_report()
        self.save_results_to_json()

    def print_report(self):
        """
        Print a structured report of the crawl results.
        If no items are found in a category, print 'None'.
        """
        print("\n--- Crawl Report ---")
        print(f"Total unique URLs discovered: {len(self.target_links)}")

        print("\nForms discovered:")
        if self.forms:
            for form_info in self.forms:
                print(f"URL: {form_info['url']}")
                print(f"Form:\n{form_info['form_html']}\n")
        else:
            print("None")

        print("Comments found in HTML:")
        if self.comments:
            for comment_info in self.comments:
                print(f"URL: {comment_info['url']}")
                print(f"Comment:\n{comment_info['comment']}\n")
        else:
            print("None")

        print("Version information discovered:")
        if self.versions:
            for version_info in self.versions:
                if 'source' in version_info:
                    # Entries from Server Header
                    print(f"URL: {version_info['url']}")
                    print(f"Version: {version_info['version']} (Source: {version_info['source']})\n")
                else:
                    # Entries from HTML content
                    print(f"URL: {version_info['url']}")
                    print(f"Version: {version_info['version']} (Line: {version_info['line']})\n")
        else:
            print("None")

    def save_results_to_json(self):
        """
        Save the crawl results to a JSON file named <hostname>-spider-result.json.
        """
        parsed_url = urlparse.urlparse(self.target_url)
        hostname = parsed_url.hostname.replace('.', '_') if parsed_url.hostname else "result"
        filename = f"{hostname}-spider-result.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=4)
            print(f"\nResults saved to {filename}")
        except IOError as e:
            print(f"Error saving results to JSON: {e}")

def main():
    """
    Parse command-line arguments and initiate the scanner.
    """
    parser = argparse.ArgumentParser(description="Automated Web Application Reconnaissance Tool")
    parser.add_argument("url", help="Target URL to scan (e.g., http://10.10.10.10)")
    parser.add_argument("-i", "--ignore", nargs='*', default=[], help="List of URLs to ignore")
    args = parser.parse_args()

    target_url = args.url
    ignore_links = args.ignore

    # Validate the URL
    parsed = urlparse.urlparse(target_url)
    if not parsed.scheme or not parsed.netloc:
        print("Invalid URL. Please provide a valid URL (e.g., http://10.10.10.10)")
        sys.exit(1)

    scanner = Scanner(target_url, ignore_links)
    scanner.run()

if __name__ == "__main__":
    main()
