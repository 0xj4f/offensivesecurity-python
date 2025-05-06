import re
import argparse

class FeroxCleaner:
    def __init__(self, input_path, output_path="feroxbuster-clean-list.txt"):
        self.input_path = input_path
        self.output_path = output_path
        self.status_code = "200"

    def extract_urls(self):
        clean_urls = []
        with open(self.input_path, "r") as file:
            for line in file:
                if re.match(rf"^{self.status_code}\s+GET", line):
                    parts = line.strip().split()
                    url = parts[-1]
                    clean_urls.append(url)
        return clean_urls

    def save_urls(self, urls):
        with open(self.output_path, "w") as file:
            for url in urls:
                file.write(f"{url}\n")

    def run(self):
        urls = self.extract_urls()
        self.save_urls(urls)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract 200 Status URLs from feroxbuster output")
    parser.add_argument("-f", "--file", required=True, help="Path to feroxbuster report file")
    args = parser.parse_args()

    cleaner = FeroxCleaner(args.file)
    cleaner.run()
