from .models import User
from .oauths import OAuth
from . import GOOGLE_OAUTH, FACEBOOK_OAUTH
from utils import make_response
from flask import request, url_for, redirect
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


def authenticate():
    data = request.get_json()
    email = data.get('email') or ''
    password = data.get('password') or ''

    user = User.find_one(email=email)
    if not user:
        return make_response(message='bad credential', status_code=400)

    valid_password = user.check_password(password)
    if not valid_password:
        return make_response(message='bad credential', status_code=400)

    token = create_access_token(identity=dict(email=user.email))
    user, err = user.save(token=token)
    if err:
        return make_response(errors=err, status_code=400)

    return make_response(user, message='login successfully', status_code=200)


@jwt_required
def check_login():
    identity_data = get_jwt_identity()
    email=identity_data.get('email') or ''

    user = User.find_one(email=email)
    if not user:
        return make_response(message='user not found', status_code=400)

    return make_response(user, status_code=200)


def get_users():
    users = User.find()

    return make_response(*users, status_code=200)


def register_user():
    data = request.get_json() or {}
    email = data.get('email') or ''
    password = data.get('password') or ''

    # CON DIA

    user = User(email=email)
    user.set_password(password)
    errors = user.validate()
    if errors:
        return make_response(errors=errors, status_code=400)

    user, errors = user.save()
    if errors:
        return make_response(errors=errors, status_code=400)

    return make_response(user, status_code=200)


def exchange_for_tokens():
    auth = OAuth(request=request).get_auth()
    email = auth.email
    if not email:
        return make_response(errors=auth.note, status_code=400)

    token = create_access_token(identity=dict(email=email))
    user = User.find_one(email=email)
    if not user:
        user = User(
            email=email,
            token=token,
            credentials={auth.provider: auth.credential},
        )
        err = user.validate()
        if err:
            return make_response(errors=err, status_code=400)

        user, err = user.save()
        if err:
            return make_response(errors=err, status_code=400)
    else:
        user.credentials.update({auth.provider: auth.credential})
        user, err = user.save()
        if err:
            return make_response(errors=err, status_code=400)

    return make_response(user)


def login_with_google():
    base_url = url_for('exchange_for_tokens', _external=True)
    login_url = OAuth(GOOGLE_OAUTH).get_login_url(base_url)
    if not login_url:
        return make_response(errors='cannot get login url')

    return make_response(login_url)


def login_with_facebook():
    base_url = url_for('exchange_for_tokens', _external=True)
    login_url = OAuth(FACEBOOK_OAUTH).get_login_url(base_url)
    if not login_url:
        return make_response(errors='cannot get login url')

    return make_response(login_url)


def check_response():
    data = {}
    data.update(
        dict(
            json=request.get_json() or {},
            query_params=request.args or {},
            jwt_identity=get_jwt_identity(),
        )
    )

    return make_response(data)



