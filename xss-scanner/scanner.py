import requests
import re
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
]


class Scanner:
    def __init__(self, url, ignore_links) -> None:
        self.session = requests.Session()
        self.set_user_agent()
        self.target_url = url
        self.target_links = []
        self.ignore_links = ignore_links
        self.reports = {
            "target": "",
            "directory": {"crawl": [], "traversal": []},
            "xss": [{"url": "", "form": "", "payload": ""}],
        }

    def set_user_agent(self):
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

    def extract_links_from(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.text)

    def crawl(self, url=None):
        if url == None:
            url = self.target_url

        href_links = self.extract_links_from(url)
        # print("url:", url)
        # print("href_links:", href_links)
        for link in href_links:
            # parsed_link = urlparse.urljoin(url, link)
            parsed_link = urlparse.urljoin(self.target_url + "/", link)
            print("parsed_link: ",parsed_link)
            
            if link in [".", ".."]:
                continue

            if "#" in parsed_link:
                parsed_link = parsed_link.split("#")[0]
                
            # if "/dvwa/dvwa/" in parsed_link:
            #     continue
            # static
            if any(parsed_link.endswith(ext) for ext in [".css", ".js", ".ico", ".jpg", ".png", ".gif", ".svg"]):
                continue


            if (
                self.target_url in parsed_link
                and parsed_link not in self.target_links
                and parsed_link not in self.ignore_links
            ):
                self.target_links.append(parsed_link)
                print(parsed_link)
                self.crawl(parsed_link)

    def extract_csrf_token(self, session, url):
        response = session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # ALWAYS CHECK FOR CSRF FIELD this is DVWA
        token = soup.find("input", {"name": "user_token"})["value"]
        return token

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, features="html.parser")
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        method = form.get("method")
        post_url = urlparse.urljoin(url, action)

        input_list = form.findAll("input")
        post_data = {}
        for input in input_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value

            post_data[input_name] = input_value
        if method == "post":
            return self.session.post(post_url, data=post_data)
        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)

            for form in forms:
                print(f"[+] Testing form in: {link}")
                is_vulnerable_to_xss = self.test_xss_in_form(form=form, url=link)
                if is_vulnerable_to_xss:
                    print(f"\n[***] XSS Discovered in: {link}")
                    print(form)
                    print("===================================\n")

            if "=" in link:
                print(f"[+] Testing Link: {link}")
                is_vulnerable_to_xss = self.test_xss_in_link(link)
                if is_vulnerable_to_xss:
                    print(f"\n[***] XSS Discovered in: {link}")

    def test_xss_in_link(self, url):
        xss_payload = "<sCript>alert('XSS PAYLOAD')</scriPt>"
        url = url.replace("=", f"={xss_payload}")
        response = self.session.get(url=url)
        return xss_payload in response.text

    def test_xss_in_form(self, form, url):
        xss_payload = "<sCript>alert('XSS PAYLOAD')</scriPt>"
        response = self.submit_form(form=form, value=xss_payload, url=url)
        return xss_payload in response.text


def dvwa_scan():
    # example attack if there's authentication
    # dvwa target
    # docker run --rm -it -p 80:80 vulnerables/web-dvwa
    # target_url = "http://localhost"  # dvwa
    # links_to_ignore = ["http://localhost/logout.php"]

    target_url = "https://d4jefcoeodr48.cloudfront.net/dvwa"
    links_to_ignore = ["https://d4jefcoeodr48.cloudfront.net/dvwa/logout.php"]
    
    
    vuln_scanner = Scanner(url=target_url, ignore_links=links_to_ignore)
    login = f"{target_url}/login.php"
    token = vuln_scanner.extract_csrf_token(vuln_scanner.session, url=login)
    print("csrf_token: ", token)
    dvwa_login = {
        "username": "admin",
        "password": "password",
        "Login": "submit",
        "user_token": token,
    }
    vuln_scanner.session.post(login, data=dvwa_login)

    # automated discovery
    vuln_scanner.crawl()
    vuln_scanner.run_scanner()


def example_scan():
    # example attack
    # if no authentication
    # target_url = "http://192.168.254.109:2368/"
    target_url = "https://blog.chardskarth.me/"
    # "https://blog.chardskarth.me/"
    links_to_ignore = ["https://localhost/logout.php"]
    vuln_scanner = Scanner(url=target_url, ignore_links=links_to_ignore)
    # automated discovery
    vuln_scanner.crawl()
    vuln_scanner.run_scanner()


if __name__ == "__main__":
    dvwa_scan()
    # example_scan()
