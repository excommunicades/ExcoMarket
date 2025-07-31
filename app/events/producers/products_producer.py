import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()
rabbit_mq = os.getenv("RABBIT_MQ_HOST", "rabbitmq")

def send_new_product_event(product):

    """
    Publishes a product event to RabbitMQ 'products' fanout exchange with product details
    (seller_id, name, price, description) serialized as JSON for subscriber notifications.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_mq))
    channel = connection.channel()
    channel.exchange_declare(exchange='products', exchange_type='fanout')

    message = json.dumps({
        "seller_id": product.seller_id,
        "name": product.name,
        "price": product.price,
        "description": product.description
    })

    channel.basic_publish(exchange='products', routing_key='', body=message)
    connection.close()
