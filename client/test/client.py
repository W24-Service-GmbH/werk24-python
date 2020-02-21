import os

from dotenv import load_dotenv

from werk24.sdk.client import W24Client

# load the environment from the .env file
load_dotenv()

# Create a new instance of the Client and login
w24_client = W24Client(
    os.getenv("W24IO_SERVER"))

w24_client.register(
    os.getenv("W24IO_COGNITO_REGION"),
    os.getenv("W24IO_COGNITO_IDENTITY_POOL_ID"),
    os.getenv("W24IO_COGNITO_CLIENT_ID"),
    os.getenv("W24IO_COGNITO_CLIENT_SECRET"),
    os.getenv("W24IO_COGNITO_USERNAME"),
    os.getenv("W24IO_COGNITO_PASSWORD"))
