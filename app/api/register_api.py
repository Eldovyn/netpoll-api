from flask import Blueprint, request, current_app
from ..controllers import UserController
import os

register_router = Blueprint("register_router", __name__)
user_controller = UserController()


@register_router.post("/netpoll/register")
async def user_register():
    data = request.json
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")
    avatar = os.path.join(current_app.root_path, "static/image/avatar.jpg")
    return await UserController().user_register(email, username, password, avatar)
