from flask import Blueprint, request
from ..controllers import PollingController
from flask_jwt_extended import jwt_required, get_jwt_identity

polling_router = Blueprint("polling_router", __name__)
polling_controller = PollingController()


@polling_router.post("/netpoll/polling")
@jwt_required()
async def add_polling():
    current_user = get_jwt_identity()
    data = request.json
    title = data.get("title", "")
    answer = data.get("answer", [])
    private = data.get("private", False)
    multi_choice = data.get("multi_choice", False)
    disable_comment = data.get("disable_comment", False)
    return await polling_controller.add_polling(
        current_user, title, answer, private, multi_choice, disable_comment
    )


@polling_router.get("/netpoll/polling")
@jwt_required()
async def get_polling():
    current_user = get_jwt_identity()
    data = request.args
    polling_id = data.get("polling_id", "")
    return await polling_controller.get_polling(current_user, polling_id)


@polling_router.get("/netpoll/my-polling")
@jwt_required()
async def get_my_polling():
    current_user = get_jwt_identity()
    data = request.args
    per_page = data.get("per_page", "5")
    page = data.get("page", "5")
    current_page = data.get("current_page", "0")
    return await polling_controller.get_my_polling(
        current_user, per_page, page, current_page
    )
