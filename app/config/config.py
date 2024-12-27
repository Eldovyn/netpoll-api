from dotenv import load_dotenv
import os

load_dotenv()

database_mongodb = os.getenv("DATABASE_MONGODB")
database_mongodb_url = os.getenv("DATABASE_MONGODB_URL")
database_postgres_url = os.getenv("DATABASE_POSTGRES_URL")
secret_key = os.getenv("SECRET_KEY_JWT")
todoplus_url = os.getenv("TODOPLUS_URL")
todoplus_api_url = os.getenv("TODOPLUS_API_URL")
secret_key_reset_password = os.getenv("SECRET_KEY_RESET_PASSWORD")
salt_reset_password = os.getenv("SALT_RESET_PASSWORD")
secret_key_account_active_web = os.getenv("SECRET_KEY_ACCOUNT_ACTIVE_WEB")
salt_account_active_web = os.getenv("SALT_ACCOUNT_ACTIVE_WEB")
secret_key_account_active_email = os.getenv("SECRET_KEY_ACCOUNT_ACTIVE_EMAIL")
salt_account_active_email = os.getenv("SALT_ACCOUNT_ACTIVE_EMAIL")
smtp_email = os.getenv("SMTP_EMAIL")
smtp_password = os.getenv("SMTP_PASSWORD")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")
broker_url = os.getenv("BROKER_URL")
result_backend = os.getenv("RESULT_BACKEND")
allowed_extensions = os.getenv("ALLOWED_EXTENSIONS").split(",")
