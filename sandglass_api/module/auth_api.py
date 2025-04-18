from datetime import timedelta

from flask import request, Blueprint, jsonify, current_app
from flask_jwt_extended import create_access_token, set_access_cookies, unset_access_cookies
from mongoengine import QuerySet

from sandglass_api.models.user import User
from sandglass_api.util import salting

auth_api = Blueprint('auth_api', __name__)


@auth_api.get('/token')
def login():
    """
    Acquire a fresh JWT token.
    """
    query_set: QuerySet = User.objects(email=request.args['email'])
    user: User = query_set.first()

    if (user is not None
            and user.pwd == salting(request.args['pwd'], user.pwd_salt.hex)):
        access_token = create_access_token(
            identity=user,
            fresh=timedelta(
                seconds=current_app.config['JWT_EXPIRE_TIME']
                        * current_app.config['JWT_INVALIDATE_FRESHNESS_FACTOR']
            ),
            expires_delta=timedelta(seconds=current_app.config['JWT_EXPIRE_TIME'])
        )
        res = jsonify(access_token=access_token, user_id=str(user.id))
        set_access_cookies(res, access_token, max_age=current_app.config['JWT_EXPIRE_TIME'])
        # TODO: 缓存控制
        return res
    else:
        return "Invalid Email or Password.", 401


@auth_api.delete('/token')
def logout():
    """
    Delete tokens saved in cookies.
    """
    response = jsonify("Successfully logged out.")
    unset_access_cookies(response)
    return response, 204
