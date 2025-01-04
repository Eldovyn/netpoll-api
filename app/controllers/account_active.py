from flask import jsonify, render_template, redirect, url_for, request
import datetime
from ..databases import AccountActiveDatabase, UserDatabase
from ..utils import TokenAccountActiveEmail, TokenAccountActiveWeb, generate_id
from ..config import netpoll_url
from ..task import send_email_task


class AccountActiveController:
    @staticmethod
    async def user_account_active_page(token):
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if len(token.strip()) == 0:
            return redirect(f"{netpoll_url}not-found")
        if not (valid_token := await TokenAccountActiveWeb.get(token)):
            return redirect(f"{netpoll_url}not-found")
        if not (
            user := await AccountActiveDatabase.get(
                "account_active", user_id=valid_token["user_id"], token_web=token
            )
        ):
            return redirect(f"{netpoll_url}not-found")
        if user.token_web != token:
            return redirect(f"{netpoll_url}not-found")
        if user.expired_at <= int(created_at):
            await AccountActiveDatabase.delete(
                "user_id", user_id=valid_token["user_id"]
            )
            return redirect(f"{netpoll_url}not-found")
        return render_template(
            "account_active/verification.html",
            user=user.user,
            host_url=request.host_url,
            netpoll_url=netpoll_url,
        )

    @staticmethod
    async def re_send_user_account_active(email):
        errors = {}
        if len(email.strip()) == 0:
            errors["email"] = ["email cannot be empty"]
        if errors:
            return (
                jsonify(
                    {
                        "message": "data is not valid",
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
                    }
                ),
                409,
            )
        if not (
            user_token := await AccountActiveDatabase.get(
                "user_id", user_id=user.user_id
            )
        ):
            return (
                jsonify({"message": "user not found"}),
                404,
            )
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if user_token.expired_at <= int(created_at):
            await AccountActiveDatabase.delete("user_id", user_id=user.user_id)
            return (
                jsonify({"message": "user not found"}),
                404,
            )
        expired_at = created_at + 300
        email_token = await TokenAccountActiveEmail.insert(
            f"{user.user_id}", int(created_at)
        )
        web_token = await TokenAccountActiveWeb.insert(
            f"{user.user_id}", int(created_at)
        )
        await AccountActiveDatabase.update(
            "token",
            token_email=email_token,
            token_web=web_token,
            expired_at=expired_at,
            updated_at=created_at,
            user_id=user_token.user_id,
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
        <a href="{url_for('account_active_router.account_active_email_verification', token=email_token, _external=True)}">
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
    async def user_account_active(email):
        errors = {}
        if len(email.strip()) == 0:
            errors["email"] = ["email cannot be empty"]
        if errors:
            return (
                jsonify(
                    {
                        "message": "data is not valid",
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
        <a href="{url_for('account_active_router.account_active_email_verification', token=email_token, _external=True)}">
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
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        if len(token.strip()) == 0:
            return redirect(f"{netpoll_url}not-found")
        valid_token = await TokenAccountActiveEmail.get(token)
        if not valid_token:
            return redirect(f"{netpoll_url}not-found")
        if not (
            token := await AccountActiveDatabase.get(
                "account_active_email",
                user_id=valid_token["user_id"],
                token_email=token,
            )
        ):
            return redirect(f"{netpoll_url}not-found")
        if token.expired_at <= int(created_at):
            await AccountActiveDatabase.delete(
                "user_id", user_id=valid_token["user_id"]
            )
            return redirect(f"{netpoll_url}not-found")
        user = await UserDatabase.get("user_id", user_id=valid_token["user_id"])
        await AccountActiveDatabase.update(
            "user_active", user_id=valid_token["user_id"]
        )
        return render_template(
            "account_active/account_verification.html",
            user=user,
            netpoll_url=netpoll_url,
        )
