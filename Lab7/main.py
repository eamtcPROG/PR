import requests
from bs4 import BeautifulSoup
import pika

def enqueue_resource(url, queue_name='myqueue', host='localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=url)
    connection.close()

def get_queue_size(channel, queue_name):
    method_frame = channel.queue_declare(queue=queue_name, passive=True)
    return method_frame.method.message_count

def scrape_and_enqueue(base_url, queue_name='myqueue', pages_limit=None, starting_page=1):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    for current_page in range(starting_page, starting_page + (pages_limit or 1)):
        response = requests.get(base_url + "?page={}".format(current_page))
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select(".block-items__item__title[href]"):
                item_href = item['href']
                if "/booster/" not in item_href:
                    complete_url = "https://999.md" + item_href
                    enqueue_resource(complete_url, queue_name)
        else:
            print(f"Failed to retrieve page {current_page}: {response.status_code}")

    queue_size = get_queue_size(channel, queue_name)
    print(f"Number of elements in the queue: {queue_size}")
    connection.close()

if __name__ == "__main__":
    scrape_and_enqueue("https://m.999.md/ro/list/sports-health-and-beauty/sports-clubs", pages_limit=1)
