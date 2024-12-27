from flask import jsonify, Response
from ..databases import UserDatabase


class ImageController:
    @staticmethod
    async def get_avatar(user_id, avatar_id):
        errors = {}
        if len(user_id.strip()) == 0:
            errors["user_id"] = ["user id cannot be empty"]
        if len(avatar_id.strip()) == 0:
            errors["avatar_id"] = ["avatar id cannot be empty"]
        if errors:
            return jsonify({"message": "input invalid", "errors": errors}), 400
        if not (user := await UserDatabase.get("user_id", user_id=user_id)):
            return jsonify({"message": "user not found"}), 404
        return Response(user.user_avatar.avatar, mimetype="image/png"), 200
