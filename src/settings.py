import os

TOKEN = os.environ.get('TOKEN')
APP_NAME = os.environ.get('APP_NAME')
PORT = int(os.environ.get('PORT', 5000))
DB_URI = os.environ.get('DB_URI')