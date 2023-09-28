import requests
from bs4 import BeautifulSoup
import json


def extractInfo(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    rusult = {}

    title = soup.find('h1', itemprop='name')
    if title:
        rusult['Title'] = title.text

    desc = soup.find('div', itemprop='description')
    if desc:
        rusult['Description'] = desc.text

    price = soup.find(
        'span', class_='adPage__content__price-feature__prices__price__value')
    currency = soup.find('span', itemprop='priceCurrency')
    if price:
        if price.text.find('negociabil') != -1:
            rusult['Price'] = price.text
        else:
            rusult['Price'] = price.text + ' ' + currency.get('content')

    country = soup.find('meta', itemprop='addressCountry')
    locality = soup.find('meta', itemprop='addressLocality')
    if country and locality:
        rusult['Location'] = locality.get(
            'content') + ', ' + country.get('content')

    info = {}
    views = soup.find('div', class_='adPage__aside__stats__views')
    if views:
        info['Views'] = views.text
    date = soup.find('div', class_='adPage__aside__stats__date')
    if date:
        info['Update Date'] = date.text
    type = soup.find('div', class_='adPage__aside__stats__type')
    if type:
        info['Ad Type'] = type.text
    ownerUsername = soup.find(
        'a', class_='adPage__aside__stats__owner__login buyer_experiment  has-reviews')
    if ownerUsername:
        info['Owner Username'] = ownerUsername.text
    rusult['Ad Info'] = info

    generalDiv = soup.find('div', class_='adPage__content__features__col')
    general = {}
    liElements = generalDiv.find_all('li')
    for li in liElements:
        keyElement = li.find('span', class_='adPage__content__features__key')
        valueElement = li.find(
            'span', class_='adPage__content__features__value')
        if keyElement and valueElement:
            key = keyElement.text.strip()
            value = valueElement.text.strip()
            general[key] = value
    rusult['General Info'] = general

    featuresDiv = soup.find(
        'div', class_='adPage__content__features__col grid_7 suffix_1')
    features = {}
    liElements = featuresDiv.find_all('li')
    for li in liElements:
        keyElement = li.find('span', class_='adPage__content__features__key')
        valueElement = li.find(
            'span', class_='adPage__content__features__value')
        if keyElement and valueElement:
            key = keyElement.text.strip()
            value = valueElement.text.strip()
            features[key] = value
    rusult['Features'] = features

    print(json.dumps(rusult, indent=4, ensure_ascii=False))

    return rusult


url = "https://999.md/ro/77310177"
extractInfo(url)