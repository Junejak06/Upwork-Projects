import httpx
from bs4 import BeautifulSoup

def elements_present(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for each button with specific class and text
    required_elements = ["Passing", "Rushing", "Receiving"]
    
    return all(soup.find('button', class_='btn btn-sm', string=element) for element in required_elements)

# Updated list of rotating proxies
proxies_list = [
    "http://38.62.220.203:3128"
]

# Headers for the requests
headers = {
   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Referer": "https://www.google.com/"
}

# Get the URL and use rotating proxy
url = 'https://ny.wynnbet.com/event/15543847'
final_urls = []

for proxy in proxies_list:
    try:
        with httpx.Client(proxies={"http://": proxy, "https://": proxy}, headers=headers, timeout=10.0) as client:
            # Here, you're using the headers in the request
            response = client.get(url, headers=headers)
            print(response)

            html_content = response.text
            if elements_present(html_content):
                base_url = url.rsplit('/', 1)[0]
                final_urls.extend([base_url + "/passing?", base_url + "/rushing?", base_url + "/receiving?"])
            break
    except (httpx.ProxyError, httpx.RequestTimeout):
        print(f"Proxy {proxy} failed or timed out. Moving to the next one.")
        continue

for f_url in final_urls:
    print(f_url)

