from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    # can be useful in future to process exceptions
    return exception_handler(exc, context)
