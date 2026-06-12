import json


def dumps(data):
    return json.dumps(data, ensure_ascii=False)


def loads(data):
    if not data:
        return {}
    return json.loads(data)