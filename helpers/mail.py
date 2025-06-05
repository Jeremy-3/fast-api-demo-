from fastapi_mail import FastMail,ConnectionConfig
from pydantic import EmailStr
from dotenv import load_dotenv
import os

# load env variables
load_dotenv()

# configure mail settings
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT","587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

# creating a fastmail instance 
fm = FastMail(conf)

