import bs4
import requests
import json
import pika

def load_urls():
    try:
        with open("url.json", "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []

def parse_urls(url, maxNumPage=None, startPage=1):
    unique_urls = set(load_urls())

    for page in range(startPage, startPage + maxNumPage):
        response = requests.get(url.format(page))

        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            links = soup.select(".block-items__item__title")

            for link in links:
                if "/booster/" not in link.get("href"):
                    url = "https://999.md" + link.get("href")
                    unique_urls.add(url)
                    append_to_queue(url)

        else:
            print(f"Failed to retrieve the web page. Status code: {response.status_code}")

    unique_urls_list = list(unique_urls)
    with open("url.json", "w", encoding="utf-8") as json_file:
        json.dump(unique_urls_list, json_file, indent=4, ensure_ascii=False)

    return unique_urls_list


def append_to_queue(url):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='myqueue')

    channel.basic_publish(exchange='', routing_key='myqueue', body=url)

    connection.close()

if __name__ == "__main__":
    parse_urls("https://m.999.md/ro/list/musical-instruments/amplifiers", maxNumPage=2)