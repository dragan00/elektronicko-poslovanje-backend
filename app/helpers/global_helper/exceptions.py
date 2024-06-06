from rest_framework.exceptions import APIException

class NotFound(APIException):
    status_code = 400
    default_detail = 'Bad Request'
    default_code = 'bad_request'

def api_exc(msg, code=400):
    exc = APIException(msg)
    exc.status_code = code
    return exc