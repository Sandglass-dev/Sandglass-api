from datetime import timedelta

from flask import request, Blueprint, jsonify
from flask_jwt_extended import create_access_token, set_access_cookies, unset_access_cookies
from mongoengine import QuerySet

from sandglass_api.config import JWT_EXPIRE_TIME, JWT_INVALIDATE_FRESHNESS_FACTOR
from sandglass_api.models.user import User
from sandglass_api.util import salting

auth_api = Blueprint('auth_api', __name__)


@auth_api.post('/token')
def login():
    req = request.json

    requested_email = req['email']
    requested_pwd = req['pwd']

    query_set: QuerySet = User.objects(email=requested_email)
    user: User = query_set.first()
    if user is not None and user.pwd == salting(requested_pwd, user.pwd_salt.hex):
        access_token = create_access_token(identity=user,
                                           fresh=timedelta(seconds=JWT_EXPIRE_TIME * JWT_INVALIDATE_FRESHNESS_FACTOR),
                                           expires_delta=timedelta(seconds=JWT_EXPIRE_TIME))
        res = jsonify(access_token=access_token)
        set_access_cookies(res, access_token)
        return res
    else:
        return "Invalid Email or Password.", 401


@auth_api.delete('/token')
def logout():
    response = jsonify("Successfully logged out.")
    unset_access_cookies(response)
    return response
