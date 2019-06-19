from .models import User
from utils import make_response
from flask.views import MethodView
from flask import request


class UserAPI(MethodView):
    def get(self):
        users = User.find()

        return make_response(*users, status_code=200)


def register_user():
    data = request.get_json(force=True)
    username = data.get('username')

    user = User(username=username)
    errors = user.validate()
    if errors:
        return make_response(errors=errors, status_code=400)

    user, errors = user.save()
    if errors:
        return make_response(errors=errors, status_code=400)

    return make_response(user, status_code=200)

