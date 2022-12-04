import ssl
import pika
from urllib.parse import urlparse, unquote


def get_pika_connection_params(mq_url: str, client_properties: dict):
    """
    Note: We are decoding as pika takes in plain credentials and does encoding by itself
    """
    parsed_url = urlparse(mq_url)
    credentials = pika.PlainCredentials(username=unquote(parsed_url.username),
                                        password=unquote(parsed_url.password))
    protocol = parsed_url.scheme

    # https://pika.readthedocs.io/en/stable/modules/parameters.html#connectionparameters
    if protocol == "amqps":
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        return pika.ConnectionParameters(
            host=parsed_url.hostname,
            port=parsed_url.port,
            credentials=credentials,
            client_properties=client_properties,
            ssl_options=pika.SSLOptions(context=ssl_context)
        )

    return pika.ConnectionParameters(
        host=parsed_url.hostname,
        port=parsed_url.port,
        credentials=credentials,
        client_properties=client_properties,
    )

