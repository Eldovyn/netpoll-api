from flask import Blueprint, request
from ..controllers import ResetPasswordController

reset_password_router = Blueprint("reset_password_router", __name__)
reset_password_controller = ResetPasswordController()


@reset_password_router.post("/netpoll/reset-password")
async def user_reset_password():
    data = request.json
    email = data.get("email", "")
    return await reset_password_controller.user_reset_password(email)


@reset_password_router.patch("/netpoll/re-send/reset-password")
async def re_send_user_reset_password():
    data = request.json
    email = data.get("email", "")
    return await reset_password_controller.re_send_user_reset_password(email)


@reset_password_router.route(
    "/netpoll/reset-password/<string:token>", methods=["GET", "POST"]
)
async def link_reset_password(token):
    return await reset_password_controller.link_reset_password(token)


@reset_password_router.get("/netpoll/reset-password/page-reset-password")
async def account_reset_password_page():
    data = request.args
    token = data.get("token", "")
    return await reset_password_controller.user_account_reset_password_page(token)
