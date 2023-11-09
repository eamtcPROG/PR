import pika
import bs4
import requests
from threading import Thread, Lock
from tinydb import TinyDB


db = TinyDB('db.json', indent=4, ensure_ascii=False)
lock = Lock()
processed_urls = set()

def parser(ch, method, properties, body, num):
    url = body.decode()

    response = requests.get(url)

    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        title = soup.find('header', {"class": "adPage__header"}).text

        price_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__value"})
        if price_element:
            price = price_element.text
        else:
            price = "Price not found"

        currency_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__currency"})
        if currency_element:
            currency = currency_element.text
        else:
            currency = ""

        description_element = soup.find('div', {"class": "adPage__content__description grid_18", "itemprop": "description"})
        if description_element:
            description = description_element.text
        else:
            description = "Description not found"

        item_data = {
            "title": title,
            "price": price + currency,
            "description": description,
        }

        with lock:
            db.insert(item_data)

        print(f"Consumer processing URL: {url}")

    else:
        print(f"Failed {url}. Status code: {response.status_code}")

def process_data(num):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='myqueue')

    channel.basic_consume(queue='myqueue', on_message_callback=lambda ch, method, properties, body: parser(ch, method, properties, body, num), auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    num = 7

    print(f'{num} consumers are processing URLs concurrently.')

    threads = []

    for i in range(num):
        thread = Thread(target=process_data, args=(i,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()