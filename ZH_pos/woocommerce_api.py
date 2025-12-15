# ZH_pos/woocommerce_api.py
import os
from woocommerce import API

wcapi = API(
    url=os.getenv("WC_STORE_URL"),
    consumer_key=os.getenv("WC_CONSUMER_KEY"),
    consumer_secret=os.getenv("WC_CONSUMER_SECRET"),
    version="wc/v3",
    timeout=30
)
