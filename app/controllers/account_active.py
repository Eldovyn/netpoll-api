from flask import jsonify, render_template, redirect, url_for
import datetime
from ..databases import AccountActiveDatabase, UserDatabase
from ..utils import TokenAccountActiveEmail, TokenAccountActiveWeb, generate_id
from ..config import todoplus_url
from ..task import send_email_task


class AccountActiveController:
    @staticmethod
    async def user_account_active_page(token):
        if len(token.strip()) == 0:
            return (
                jsonify(
                    {"message": "input invalid", "errors": ["token cannot be empty"]}
                ),
                400,
            )
        if not (valid_token := await TokenAccountActiveWeb.get(token)):
            return jsonify({"message": "invalid token"}), 404
        if not (
            user := await AccountActiveDatabase.get(
                "account_active", user_id=valid_token["user_id"], token_web=token
            )
        ):
            return jsonify({"message": "invalid token"}), 404
        if user.token_web != token:
            return jsonify({"message": "invalid token"}), 404
        return (
            jsonify(
                {
                    "message": "success get page",
                    "data": {
                        "username": user.user.username,
                        "email": user.user.email,
                        "user_id": user.user.user_id,
                        "is_active": user.user.is_active,
                        "avatar": f'{url_for("image_router.get_avatar", user_id=user.user.user_id, avatar_id=user.user.user_avatar.avatar_id, _external=True)}',
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                    },
                }
            ),
            200,
        )

    @staticmethod
    async def user_account_active(email):
        errors = {}
        if len(email.strip()) == 0:
            errors["email"] = ["email cannot be empty"]
        if errors:
            return (
                jsonify(
                    {
                        "message": "input is not valid",
                        "errors": errors,
                    }
                ),
                400,
            )
        if not (user := await UserDatabase.get("email", email=email)):
            return (
                jsonify({"message": "user not found"}),
                404,
            )
        if user.is_active:
            return (
                jsonify(
                    {
                        "message": "user already active",
                        "data": {
                            "user_id": user.user_id,
                            "username": user.username,
                            "email": user.email,
                            "is_active": user.is_active,
                        },
                    }
                ),
                409,
            )
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        expired_at = created_at + 300
        email_token = await TokenAccountActiveEmail.insert(
            f"{user.user_id}", int(created_at)
        )
        web_token = await TokenAccountActiveWeb.insert(
            f"{user.user_id}", int(created_at)
        )
        await AccountActiveDatabase.insert(
            generate_id(),
            f"{user.user_id}",
            email_token,
            web_token,
            int(expired_at),
            created_at,
        )
        send_email_task.apply_async(
            args=[
                "Account Active",
                [user.email],
                f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
</head>
<body>
    <p>Hello {user.username},</p>
    <p>Someone has requested a link to verify your account, and you can do this through the link below.</p>
    <p>
        <a href="{todoplus_url}user-verification?token={email_token}">
            Click here to activate your account
        </a>
    </p>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>
                """,
                "account active",
            ],
        )
        return (
            jsonify(
                {
                    "message": "success send email active account",
                    "data": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "token": web_token,
                    },
                }
            ),
            201,
        )

    @staticmethod
    async def user_account_active_verification(token):
        if len(token.strip()) == 0:
            return (
                jsonify(
                    {
                        "message": "invalid input",
                        "errors": {"token": ["token cannot be empty"]},
                    }
                ),
                404,
            )
        valid_token = await TokenAccountActiveEmail.get(token)
        if not valid_token:
            return jsonify({"message": "invalid token"}), 404
        if not (
            token := await AccountActiveDatabase.get(
                "account_active_email",
                user_id=valid_token["user_id"],
                token_email=token,
            )
        ):
            return jsonify({"message": "invalid token"}), 404
        user = await UserDatabase.get("user_id", user_id=valid_token["user_id"])
        await AccountActiveDatabase.update("user_id", user_id=valid_token["user_id"])
        return (
            jsonify(
                {
                    "message": "success send email active account",
                    "data": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                    },
                }
            ),
            201,
        )
