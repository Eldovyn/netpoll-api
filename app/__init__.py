from flask import Flask, jsonify
from .models import UserModel
from .celery_app import celery_init_app
from .models import (
    ResetPasswordModel,
    UserModel,
    AccountActiveModel,
    TokenBlocklistModel,
)
from celery.schedules import crontab
import datetime
from .config import (
    broker_url,
    result_backend,
    secret_key,
    smtp_email,
    smtp_password,
    smtp_host,
    smtp_port,
    database_postgres_url,
)
from .database import db
from .jwt import jwt
from .mail import mail


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        CELERY=dict(
            broker_url=broker_url,
            result_backend=result_backend,
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    app.config["JWT_SECRET_KEY"] = secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    app.config["MAIL_SERVER"] = smtp_host
    app.config["MAIL_PORT"] = smtp_port
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = smtp_email
    app.config["MAIL_PASSWORD"] = smtp_password
    app.config["MAIL_DEFAULT_SENDER"] = smtp_email
    app.config["SQLALCHEMY_DATABASE_URI"] = database_postgres_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    global celery_app
    celery_app = celery_init_app(app)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    @celery_app.task(name="delete_token_task")
    def delete_token_task():
        expired_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        if data := db.session.query(ResetPasswordModel).all():
            for item1 in data:
                if item1.expired_at <= expired_at:
                    db.session.delete(item1)
                    db.session.commit()
        if data := db.session.query(AccountActiveModel).all():
            for item2 in data:
                if item2.expired_at <= expired_at:
                    db.session.delete(item2)
                    db.session.commit()
        return f"delete token at {int(datetime.datetime.now(datetime.timezone.utc).timestamp())}"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "delete_token_task",
            "schedule": crontab(minute="*/5"),
        },
    }

    with app.app_context():
        from .api.register_api import register_router
        from .api.login_api import login_router
        from .api.me_api import me_router
        from .api.update_profile_api import update_profile_router
        from .api.reset_password_api import reset_password_router
        from .api.account_active import account_active_router
        from .api.image_api import image_router
        from .api.logout import logout_router

        app.register_blueprint(register_router)
        app.register_blueprint(login_router)
        app.register_blueprint(me_router)
        app.register_blueprint(update_profile_router)
        app.register_blueprint(reset_password_router)
        app.register_blueprint(account_active_router)
        app.register_blueprint(image_router)
        app.register_blueprint(logout_router)

        db.create_all()

    @app.after_request
    async def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = (
            db.session.query(TokenBlocklistModel.token_id).filter_by(jti=jti).scalar()
        )
        return token is not None

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.user_id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return UserModel.query.filter(
            UserModel.user_id == identity, UserModel.is_active == True
        ).first()

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"meessage": "token has been revoked. please login again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"message": f"token is invalid. {reason}"}), 422

    @jwt.unauthorized_loader
    def missing_authorization_header_callback(reason):
        return (
            jsonify({"message": "authorization header is missing or invalid."}),
            401,
        )

    @jwt.user_lookup_error_loader
    def missing_token_callback(jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return (
            jsonify(
                {
                    "message": "user account is inactive",
                    "data": {"user_id": identity},
                }
            ),
            403,
        )

    return app
