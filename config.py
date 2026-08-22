import os

from dotenv import load_dotenv

load_dotenv()

JWT = os.getenv("PANEL_API_KEY")
URL = os.getenv("ADMIN_URL")
SOURCE_URL = os.getenv('SOURCE_URL')
SECRET_KEY = os.getenv('APP_KEY')

DATABASE_URL=os.getenv('DATABASE_URL')

