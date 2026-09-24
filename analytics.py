from enum import StrEnum
import logfire

class Action(StrEnum):
    SIGNUP_ATTEMPTED = "signup_attempted"
    USER_SIGNED_UP = "user_signed_up"
    SIGNUP_FAILED = "signup_failed"
    LOGIN_ATTEMPTED = "login_attempted"
    USER_LOGGED_IN = "user_logged_in"
    LOGIN_FAILED = "login_failed"

    POST_CREATE_ATTEMPTED = "post_create_attempted"
    POST_CREATED = "post_created"
    POST_CREATE_FAILED = "post_create_failed"

    POST_LIKED = "post_liked"
    COMMENT_ADDED = "comment_added"
    USER_FOLLOWED = "user_followed"


def track(action: Action, user_id: int | None = None, **attrs):
    logfire.info("{action}", action=action.value, user_id=user_id, **attrs)

def track_error(action: Action, user_id: int | None = None, **attrs):
    logfire.exception("{action}", action=action.value, user_id=user_id, **attrs)