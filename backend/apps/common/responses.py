from rest_framework.response import Response


def ok(data=None, message='success', code=200):
    return Response({'code': code, 'message': message, 'data': data}, status=code)
