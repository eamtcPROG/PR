import requests
from bs4 import BeautifulSoup
# Replace with the URL of the web page you want to scrape https://999.md/ro/list/transport/cars
dir = []
for i in range(641,645):
 url = 'https://999.md/ro/list/transport/cars?page=' + str(i)
 print(url)
 #print_links(ma)
 try:
  # Send a GET request to the URL
  response = requests.get(url)

  # Check if the request was successful (status code 200)
  if response.status_code == 200:
   soup = BeautifulSoup(response.text, 'html.parser')
   print(len(soup.findAll('div', attrs={'class':'ads-list-photo-item-title'})))
  # Find all anchor (link) tags in the HTML
  # links = soup.find_all('<div class="ads-list-photo-item-title "> <a>')


   for div in soup.findAll('div', attrs={'class':'ads-list-photo-item-title'}):
    if len(div.find('a')['href']) == 0:
      exit(0)
    link = div.find('a')['href']
    if(link.startswith('/booster') == False):
     fulllink = "https://999.md"+ div.find('a')['href']
     dir.append(fulllink)
     print(fulllink)

  else:
   print(f"Failed to retrieve the web page. Status code: {response.status_code}")
 except requests.exceptions.RequestException as e:
  print(f"An error occurred during the request: {e}")

 except Exception as e:
  print(f"An unexpected error occurred: {e}")
