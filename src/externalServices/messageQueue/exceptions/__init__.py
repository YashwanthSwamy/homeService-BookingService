class PublishMessageError(Exception):
    """Exception raised when publish message failed."""
    pass


class MaxRetryPublisherConnectionError(Exception):
    """Exception raised when publish message failed."""
    pass


class QueueException(Exception):
    """Exception raised in MessageQ.
     Attributes:
         message -- explanation of the error
     """

    def __init__(self, message="unknown exception occurred in MessageQ"):
        self.message = message
        super().__init__(self.message)
