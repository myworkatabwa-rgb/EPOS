import os
import logging
from woocommerce import API

logger = logging.getLogger(__name__)

def get_wcapi():
    """
    Initialize WooCommerce API safely.
    Returns None if credentials or URL are missing.
    """
    wc_url = os.getenv("WC_STORE_URL")
    ck = os.getenv("WC_CONSUMER_KEY")
    cs = os.getenv("WC_CONSUMER_SECRET")

    if not wc_url or not ck or not cs:
        logger.warning("WooCommerce credentials are missing. API not initialized.")
        return None

    return API(
        url=wc_url,
        consumer_key=ck,
        consumer_secret=cs,
        version="wc/v3",
        timeout=30
    )
