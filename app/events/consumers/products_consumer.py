import os
import pika
import json
import redis
import asyncio
from telegram import Bot
from dotenv import load_dotenv

from main import app
from db.models import Subscription

load_dotenv()

bot_token = os.getenv("TG_BOT_TOKEN", None)
redis_host = os.getenv("REDIS_HOST", "redis")
rabbitmq_host = os.getenv("RABBIT_MQ_HOST", "rabbitmq")
redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
bot = Bot(token=bot_token)


def callback(ch, method, properties, body):

    """
    RabbitMQ callback triggered on product events: loads product data from message,
    fetches all subscribers for the seller, and asynchronously sends Telegram notifications
    to subscribers with product info.
    """

    with app.app_context():
        data = json.loads(body)
        seller_id = data["seller_id"]
        product_name = data["name"]
        product_price = data.get("price", "не указана")
        product_description = data.get("description", "нет описания")

        subs = Subscription.query.filter_by(seller_id=seller_id).all()
        for sub in subs:
            chat_id = redis_client.get(f"user:{sub.subscriber_id}:chat_id")
            if chat_id:
                asyncio.run(send_notification(chat_id, seller_id, product_name, product_price, product_description))

        ch.basic_ack(delivery_tag=method.delivery_tag)


async def send_notification(chat_id, seller_id, name, price, description):

    """
    Sends a Telegram message notifying a subscriber about a new product from a seller,
    formatting the message with product details.
    """

    message = (
    f"🔔 New item from seller #{seller_id}:\n\n"
    f"🛍 Name: {name}\n"
    f"💰 Price: {price}\n"
    f"📄 Description: {description}"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"❌ Error sending message to Telegram: {e}")


def consume():

    """
    Connects to RabbitMQ, declares a fanout exchange 'products', creates a temporary queue,
    binds it to the exchange, and starts consuming messages using the callback.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()

    channel.exchange_declare(exchange='products', exchange_type='fanout')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='products', queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()
