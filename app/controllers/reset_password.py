from ..databases import ResetPasswordDatabase, UserDatabase
from flask import jsonify, url_for, request, render_template, redirect
import datetime
from ..utils import TokenResetPasswordEmail, generate_id, TokenResetPasswordWeb
from ..config import netpoll_url
import re
from ..task import send_email_task


class ResetPasswordController:
    @staticmethod
    async def user_account_reset_password_page(token):
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if not token:
            return redirect(f"{netpoll_url}not-found")
        if not (valid_token := await TokenResetPasswordWeb.get(token)):
            return redirect(f"{netpoll_url}not-found")
        if not (
            user := await ResetPasswordDatabase.get(
                "reset_password", user_id=valid_token["user_id"]
            )
        ):
            return redirect(f"{netpoll_url}not-found")
        if user.token_web != token:
            return redirect(f"{netpoll_url}not-found")
        if user.expired_at <= int(created_at):
            await ResetPasswordDatabase.delete(
                "user_id", user_id=valid_token["user_id"]
            )
            return redirect(f"{netpoll_url}not-found")
        return render_template(
            "reset_password/reset_password.html",
            user=user.user,
            host_url=request.host_url,
            netpoll_url=netpoll_url,
        )

    @staticmethod
    async def link_reset_password(token):
        from ..bcrypt import bcrypt

        valid_token = await TokenResetPasswordEmail.get(token)
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if request.method == "GET":
            if not token:
                return redirect(f"{netpoll_url}not-found")
            if not (
                user := await ResetPasswordDatabase.get(
                    "reset_password", user_id=valid_token["user_id"]
                )
            ):
                return redirect(f"{netpoll_url}not-found")
            if user.token_email != token:
                return redirect(f"{netpoll_url}not-found")
            if user.expired_at <= int(created_at):
                await ResetPasswordDatabase.delete(
                    "user_id", user_id=valid_token["user_id"]
                )
                return redirect(f"{netpoll_url}not-found")
            return render_template("reset_password/user_reset_password.html")
        if request.method == "POST":
            form = request.form
            password = form.get("password")
            confirm_password = form.get("confirmPassword")
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
            if password != confirm_password:
                if "password" in errors:
                    errors["password"].append("passwords do not match")
                else:
                    errors["password"] = ["passwords do not match"]
            if not errors:
                created_at = int(
                    datetime.datetime.now(datetime.timezone.utc).timestamp()
                )
                password = bcrypt.generate_password_hash(password).decode("utf-8")
                await UserDatabase.update(
                    "password",
                    new_password=password,
                    user_id=valid_token["user_id"],
                    created_at=created_at,
                )
                await ResetPasswordDatabase.delete(
                    "user_id", user_id=valid_token["user_id"]
                )
                return redirect(f"{netpoll_url}login")
            return render_template(
                "reset_password/user_reset_password.html",
                errors=errors["password"],
                password=password,
                confirm_password=confirm_password,
                user_token=token,
            )

    @staticmethod
    async def re_send_user_reset_password(email):
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
        if not (
            user_token := await ResetPasswordDatabase.get(
                "token_active", user_id=user.user_id
            )
        ):
            return (
                jsonify({"message": "user not found"}),
                404,
            )
        if user_token.expired_at <= int(created_at):
            await ResetPasswordDatabase.delete("user_id", user_id=user.user_id)
            return (
                jsonify({"message": "user not found"}),
                404,
            )
        expired_at = created_at + 300
        token_email = await TokenResetPasswordEmail.insert(
            f"{user.user_id}", int(created_at)
        )
        token_web = await TokenResetPasswordWeb.insert(
            f"{user.user_id}", int(created_at)
        )
        await ResetPasswordDatabase.update(
            "token_active",
            user_id=user.user_id,
            token_email=token_email,
            token_web=token_web,
            expired_at=int(expired_at),
            updated_at=int(created_at),
        )
        send_email_task.apply_async(
            args=[
                "Reset Password Netpoll",
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
        <a href="{url_for('reset_password_router.link_reset_password', token=token_email, _external=True)}">
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
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "token": token_web,
                    },
                }
            ),
            201,
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
        token_email = await TokenResetPasswordEmail.insert(
            f"{user.user_id}", int(created_at)
        )
        token_web = await TokenResetPasswordWeb.insert(
            f"{user.user_id}", int(created_at)
        )
        if not (
            user_token := await ResetPasswordDatabase.insert(
                generate_id(),
                user.user_id,
                token_email,
                token_web,
                int(expired_at),
                int(created_at),
            )
        ):
            return (
                jsonify({"message": "email not found"}),
                404,
            )
        send_email_task.apply_async(
            args=[
                "Reset Password Netpoll",
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
        <a href="{url_for('reset_password_router.link_reset_password', token=token_email, _external=True)}">
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
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": user.email,
                        "is_active": user.is_active,
                        "token": token_web,
                    },
                }
            ),
            201,
        )
