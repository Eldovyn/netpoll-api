from flask import jsonify
from ..databases import PollingDatabase, UserDatabase
from ..utils import generate_id


class PollingController:
    @staticmethod
    async def get_polling(user_id, polling_id):
        errors = {}
        if len(polling_id.strip()) == 0:
            errors["polling_id"] = ["polling id cannot be empty"]
        if errors:
            return jsonify({"message": "input invalid", "errors": errors}), 400
        if not (user := await UserDatabase.get("user_id", user_id=user_id)):
            return jsonify({"message": "authorization invalid"}), 401
        if not (polling := await PollingDatabase.get("polling", polling_id=polling_id)):
            return (
                jsonify(
                    {"message": "polling not found", "data": {"polling_id": polling_id}}
                ),
                404,
            )
        return (
            jsonify(
                {
                    "message": "success create polling",
                    "data": {
                        "username": polling.user.username,
                        "user_id": polling.user.user_id,
                        "polling": {
                            "polling_id": polling.polling_id,
                            "title": polling.title,
                            "private": polling.private,
                            "multi_choice": polling.multi_choice,
                            "disable_comment": polling.disable_comment,
                            "created_at": polling.created_at,
                            "updated_at": polling.updated_at,
                        },
                        "answer": [
                            {
                                "answer_id": item.answer_id,
                                "answer": item.answer,
                                "created_at": item.created_at,
                                "updated_at": item.updated_at,
                            }
                            for item in polling.answers
                        ],
                    },
                }
            ),
            200,
        )

    @staticmethod
    async def add_polling(
        user_id, title, answer, private, multi_choice, disable_comment
    ):
        errors = {}
        if len(title.strip()) == 0:
            errors["title"] = ["title cannot be empty"]
        if isinstance(answer, list):
            if len(answer) == 0:
                errors["answer"] = ["answer cannot be empty"]
            if len(answer) > 5:
                if "answer" not in errors:
                    errors["answer"] = ["answer cannot be more than 5"]
                else:
                    errors["answer"].append("answer cannot be more than 5")
            for index, valuue in enumerate(answer):
                if len(valuue.strip()) == 0:
                    if "answer" not in errors:
                        errors["answer"] = [f"answer {index + 1} cannot be empty"]
                    else:
                        errors["answer"].append(f"answer {index + 1} cannot be empty")
        else:
            if "answer" not in errors:
                errors["answer"] = ["answer must be list"]
            else:
                errors["answer"].append("answer must be list")
        if not isinstance(private, bool):
            errors["private"] = ["private must be boolean"]
        if not isinstance(multi_choice, bool):
            errors["multi_choice"] = ["multi_choice must be boolean"]
        if not isinstance(disable_comment, bool):
            errors["disable_comment"] = ["disable_comment must be boolean"]
        if errors:
            return jsonify({"message": "input invalid", "errors": errors}), 400
        if not (user := await UserDatabase.get("user_id", user_id=user_id)):
            return jsonify({"message": "authorization invalid"}), 401
        polling, answer = await PollingDatabase.insert(
            generate_id(),
            user.user_id,
            title,
            answer,
            private,
            multi_choice,
            disable_comment,
        )
        return (
            jsonify(
                {
                    "message": "success create polling",
                    "data": {
                        "username": user.username,
                        "user_id": user.user_id,
                        "polling": {
                            "polling_id": polling.polling_id,
                            "title": title,
                            "private": polling.private,
                            "multi_choice": polling.multi_choice,
                            "disable_comment": polling.disable_comment,
                            "created_at": polling.created_at,
                            "updated_at": polling.updated_at,
                        },
                        "answer": [
                            {
                                "answer_id": item.answer_id,
                                "answer": item.answer,
                                "created_at": item.created_at,
                                "updated_at": item.updated_at,
                            }
                            for item in answer
                        ],
                    },
                }
            ),
            201,
        )
