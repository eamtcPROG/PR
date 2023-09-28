import requests
from bs4 import BeautifulSoup

def recursive(maxPage, startPage, fullurl, data):
    url = fullurl[startPage]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a', href=True, class_='js-item-ad'):
        link = str(link.get('href'))
        if link[1] != 'b':
            urlToUppend = 'https://999.md' + link
            data.append(urlToUppend)

    pages = soup.select('nav.paginator > ul > li > a')
    for page in pages:
        link = str('https://999.md' + page['href'])
        if link not in fullurl:
            fullurl.append(link)

    if startPage == maxPage or startPage >= len(fullurl)-1:
        print(data)
        return data
    else:
        recursive(maxPage, startPage+1, fullurl, data)


fullurl = ["https://999.md/ro/list/furniture-and-interior/upholstery"]
links = recursive(5, 0, fullurl, [])