import random
import string
import datetime


def generate_id():
    created_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    created_at_list = list(str(created_at))
    random.shuffle(created_at_list)
    random_created_at = "".join(created_at_list)
    random_string = "".join(random.choice(string.ascii_letters) for _ in range(10))
    result = f"{random_string}{random_created_at}"
    return result
