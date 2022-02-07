def generate_code(length=5):
    from random import randint
    return "".join([str(randint(0, 9)) for _ in range(length)])


def clean_phone(phone):
    return phone.replace("(", "") \
        .replace(")", "") \
        .replace(" ", "") \
        .replace("+", "") \
        .replace("-", "") \
        .replace(".", "")