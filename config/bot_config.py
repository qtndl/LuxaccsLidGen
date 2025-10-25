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
WEBHOOK_URL = "https://xn--80ah0ay.xn------c4dkrytqbkkf4adrce4a.xn--p1ai/api/webhook"  # HTTPS! Путь должен совпадать с эндпоинтом ниже

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
