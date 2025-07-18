# import re
# import argparse

# def parse_curl_command(file_path="curl.sh"):
#     with open(file_path, 'r') as file:
#         curl_command = file.read().strip()

#     # Extract URL
#     url_match = re.search(r"curl '([^']*)'", curl_command)
#     url = url_match.group(1) if url_match else None

#     # Extract headers
#     headers = dict(re.findall(r"-H '([^:]*): ([^']*)'", curl_command))

#     # Extract data
#     data_match = re.search(r"--data-raw '([^']*)'", curl_command)
#     raw_data = data_match.group(1) if data_match else None
#     data = dict(re.findall(r"([^=&]+)=([^&]*)", raw_data))

#     return url, headers, data

# if __name__ == "__main__":
#     # file_path = "curl.sh"
#     parser = argparse.ArgumentParser(description="Parse curl command from a file")
#     parser.add_argument("--curl", type=str, help="File path of the curl command file", required=True)
#     args = parser.parse_args()

#     url, headers, data = parse_curl_command(args.curl)
    
#     print("URL:", url)
#     print("Headers:", headers)
#     print("Data:", data)

# """
# TODO: 
# - try to urlparse if there's problem
# """

import re
import urllib.parse
import argparse

def parse_curl_command(file_path):
    with open(file_path, 'r') as file:
        curl_command = file.read().strip()

    # Extract URL
    url_match = re.search(r"curl '([^']*)'", curl_command)
    url = url_match.group(1) if url_match else None

    # Extract headers
    headers = dict(re.findall(r"-H '([^:]*): ([^']*)'", curl_command))

    # Extract data
    data_match = re.search(r"--data-raw '([^']*)'", curl_command)
    raw_data = data_match.group(1) if data_match else None
    decoded_data = urllib.parse.unquote_plus(raw_data)  # Decode URL-encoded form data, converting + to spaces correctly
    data = dict(re.findall(r"([^=&]+)=([^&]*)", decoded_data))

    return url, headers, data

def main():
    parser = argparse.ArgumentParser(description="Parse curl command from a file")
    parser.add_argument("--curl", type=str, help="File path of the curl command file", required=True)
    args = parser.parse_args()

    url, headers, data = parse_curl_command(args.curl)
    
    print("URL:", url)
    print("Headers:", headers)
    print("Data:", data)

if __name__ == "__main__":
    main()
