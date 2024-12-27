from flask import Blueprint, request
from ..controllers import ResetPasswordController

reset_password_router = Blueprint("reset_password_router", __name__)
reset_password_controller = ResetPasswordController()


@reset_password_router.post("/netpoll/reset-password")
async def user_reset_password():
    data = request.json
    email = data.get("email")
    return await reset_password_controller.user_reset_password(email)


@reset_password_router.route(
    "/netpoll/reset-password/<string:token>", methods=["GET", "POST"]
)
async def link_reset_password(token):
    return await reset_password_controller.user_reset_password_page(token)
