from typing import Callable
from pika.adapters.asyncio_connection import AsyncioConnection

from .services.getPikaConnectionParams import get_pika_connection_params


class Connection(AsyncioConnection):
    """ Connects to Message Q"""
    def __init__(self, connection_url: str, connection_name: str,
                 on_open_callback: Callable,
                 on_open_error_callback: Callable,
                 on_close_callback: Callable):
        client_properties = {
            'connection_name': connection_name
        }

        connection_parameters = get_pika_connection_params(connection_url, client_properties)
        super().__init__(parameters=connection_parameters,
                         on_open_callback=on_open_callback,
                         on_open_error_callback=on_open_error_callback,
                         on_close_callback=on_close_callback)

