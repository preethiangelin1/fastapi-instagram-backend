from unittest.mock import patch

from analytics import Action, track, track_error


def test_track_logs_action_and_user_context() -> None:
    with patch("analytics.logfire.info") as log_info:
        track(Action.USER_LOGGED_IN, user_id=42, method="password")

    log_info.assert_called_once_with(
        "{action}",
        action="user_logged_in",
        user_id=42,
        method="password",
    )


def test_track_error_logs_action_and_extra_context() -> None:
    with patch("analytics.logfire.exception") as log_exception:
        track_error(Action.LOGIN_FAILED, user_id=7, reason="invalid_password")

    log_exception.assert_called_once_with(
        "{action}",
        action="login_failed",
        user_id=7,
        reason="invalid_password",
    )
