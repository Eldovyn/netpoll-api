from flask import Blueprint
from ..controllers import UserController
from flask_jwt_extended import jwt_required, get_jwt

logout_router = Blueprint("logout_router", __name__)
user_controller = UserController()


@logout_router.delete("/netpoll/logout")
@jwt_required()
async def user_logout():
    jti = get_jwt()["jti"]
    return await UserController.user_logout(jti)
