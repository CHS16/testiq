import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Shubham:AkWdclGl8egae8fr@projectdb.1ad82kx.mongodb.net/intent_iq_db?retryWrites=true&w=majority&appName=ProjectDB")
DB_NAME = os.getenv("DB_NAME", "intent_iq_db")
