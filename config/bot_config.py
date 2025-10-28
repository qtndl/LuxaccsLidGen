from dotenv import dotenv_values
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import os

config = dotenv_values(os.path.join(os.path.dirname(__file__), '.env'))

TOKEN = config['api_token']
CHAT_ID = config['chat_id']

WEBHOOK_HOST = '109.69.19.111'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)

HOST = config['host']
USER = config['user']
PASSWORD = config['password']
DATABASE = config['database']
PORT = config['port']

logging.basicConfig(level=logging.INFO)

redis = Redis(host='localhost', port=6379, db=0)
storage = RedisStorage(redis)

bot = Bot(TOKEN)
dp = Dispatcher(storage=storage)
