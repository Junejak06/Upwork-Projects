import requests
from bs4 import BeautifulSoup

url = 'https://www.aliseeks.com/search/image?fskey=yBR0BBX9yMcZjkRZ3XG0&site=ali'
response = requests.get(url)

# Check the response content
print(response.text[:10000]) 