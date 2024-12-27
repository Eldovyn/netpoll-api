from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..controllers import UserController

update_profile_router = Blueprint("update_profile_router", __name__)
user_controller = UserController()


@update_profile_router.patch("/netpoll/password")
@jwt_required()
async def update_password():
    current_user = get_jwt_identity()
    data = request.json
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    return await user_controller.update_password(
        current_user, password, confirm_password
    )


@update_profile_router.patch("/netpoll/profile")
@jwt_required()
async def update_profiles():
    current_user = get_jwt_identity()
    data = request.json
    new_email = data.get("new_email")
    new_username = data.get("new_username")
    return await user_controller.update_user(current_user, new_username, new_email)


@update_profile_router.patch("/netpoll/profile/email")
@jwt_required()
async def update_email():
    current_user = get_jwt_identity()
    data = request.json
    new_email = data.get("new_email")
    return await user_controller.update_user_email(current_user, new_email)


@update_profile_router.patch("/netpoll/profile/username")
@jwt_required()
async def update_username():
    current_user = get_jwt_identity()
    data = request.json
    new_username = data.get("new_username")
    return await user_controller.update_user_username(current_user, new_username)
