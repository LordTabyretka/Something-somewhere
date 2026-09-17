from flask import request, session


_NOTIFICATION_KEY = "notification"


def create_notification(message, category, target_endpoint):
    session[_NOTIFICATION_KEY] = {
        "message": message,
        "category": category,
        "target_endpoint": target_endpoint,
    }


def consume_notification():
    notification = session.pop(_NOTIFICATION_KEY, None)

    if notification is None:
        return None

    if notification["target_endpoint"] != request.endpoint:
        return None

    return notification