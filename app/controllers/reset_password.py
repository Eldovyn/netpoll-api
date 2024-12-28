from ..databases import ResetPasswordDatabase, UserDatabase
from flask import jsonify, url_for, request, render_template, redirect
from werkzeug.security import generate_password_hash
import datetime
from ..utils import TokenResetPassword, generate_id
from ..config import netpoll_url
import re
from ..task import send_email_task


class ResetPasswordController:
    @staticmethod
    async def user_reset_password_page(token):
        valid_token = await TokenResetPassword.get(token)
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if request.method == "GET":
            if (
                not valid_token
                or not "user_id" in valid_token
                or not "created_at" in valid_token
            ):
                return jsonify({"message": "invalid token"}), 404
            if not (
                user := await ResetPasswordDatabase.get(
                    "user_id", user_id=valid_token["user_id"]
                )
            ):
                return jsonify({"message": "user not found"}), 404
            else:
                if user.token != token:
                    return jsonify({"message": "invalid token"}), 404
                if user.expired_at <= created_at:
                    await ResetPasswordDatabase.delete(
                        "user_id", user_id=valid_token["user_id"]
                    )
                    return jsonify({"message": "token expired"}), 404
            return render_template("reset_password/reset_password.html")
        if request.method == "POST":
            data = request.form
            password = data.get("password")

            errors = {}
            if len(password.strip()) == 0:
                if "password" in errors:
                    errors["password"].append("password cant be empety")
                else:
                    errors["password"] = ["password cant be empety"]
            if len(password) < 8:
                if "password" in errors:
                    errors["password"].append("minimum 8 characters")
                else:
                    errors["password"] = ["minimum 8 characters"]
            if not re.search("[a-z]", password):
                if "password" in errors:
                    errors["password"].append("password must contain lowercase")
                else:
                    errors["password"] = ["password must contain lowercase"]
            if not re.search("[A-Z]", password):
                if "password" in errors:
                    errors["password"].append("password must contain uppercase")
                else:
                    errors["password"] = ["password must contain uppercase"]
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                if "password" in errors:
                    errors["password"].append("password contains special character(s)")
                else:
                    errors["password"] = ["password contains special character(s)"]
            if not errors:
                password = generate_password_hash(password)
                await UserDatabase.update(
                    "password", new_password=password, user_id=valid_token["user_id"]
                )
                await ResetPasswordDatabase.delete(
                    "user_id", user_id=valid_token["user_id"]
                )
                return redirect(f"{netpoll_url}login")
            return render_template(
                "reset_password.html",
                errors=errors["password"],
                error_length=len(errors["password"]),
                password=password,
            )

    @staticmethod
    async def user_reset_password(email):
        if len(email.strip()) == 0:
            return (
                jsonify(
                    {
                        "message": "input invalid",
                        "errors": {"email": ["email cannot be empty"]},
                    }
                ),
                400,
            )
        if not (user := await UserDatabase.get("email", email=email)):
            return (
                jsonify({"message": "email not found"}),
                404,
            )
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        expired_at = created_at + 300
        token = await TokenResetPassword.insert(f"{user.id}", int(created_at))
        if not (
            user_token := await ResetPasswordDatabase.insert(
                generate_id(), user.user_id, token, int(expired_at), int(created_at)
            )
        ):
            return (
                jsonify({"message": "email not found"}),
                404,
            )
        send_email_task.apply_async(
            args=[
                "Reset Password TodoPlus",
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
    <p>Someone has requested a link to change your password, and you can do this through the link below.</p>
    <p>
        <a href="{url_for('reset_password_router.link_reset_password', token=token, _external=True)}">
            Click here to reset your password
        </a>
    </p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Your password won't change until you access the link above and create a new one.</p>
</body>
</html>
""",
                "reset password",
            ],
        )
        return (
            jsonify(
                {
                    "message": "success send reset password",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                    },
                }
            ),
            201,
        )
