import functools

from flask import Flask


def bind_app_context(_func=None, **root_kwargs):
    """ The root decorator function which takes flask app as parameter """

    def decorator_bind_app_context(function):
        """ Flask application bind decorator for normal function """

        @functools.wraps(function)
        def wrapper_bind(*args, **kwargs):
            """ decorator bind method which pushes the input function passed
            as parameter into the application context taken from the root """

            if 'app_getter' in root_kwargs:
                flask_app = root_kwargs['app_getter']()
            elif 'app' in root_kwargs:
                flask_app = root_kwargs['app']
            else:
                if isinstance(args[0], Flask):
                    flask_app = args[0]
                else:
                    flask_app = args[0].app
            with flask_app.app_context():
                return function(*args, **kwargs)
        return wrapper_bind

    # https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
    if _func is None:
        return decorator_bind_app_context
    else:
        return decorator_bind_app_context(_func)


def bind_app_context_for_async_function(function):
    """ Flask application bind decorator for async function as we need await
    for the response of the called function"""

    @functools.wraps(function)
    async def wrapper_bind(*args, **kwargs):
        """ decorator bind method which pushes the input function passed
            as parameter into the application context taken from the root """

        flask_app = args[0].app
        with flask_app.app_context():
            return await function(*args, **kwargs)
    return wrapper_bind

