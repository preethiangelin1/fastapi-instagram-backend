import pytest
from pydantic import ValidationError

from schemas import FollowRequestUpdate, PostCreate, UserCreate


def test_user_create_accepts_valid_user_data() -> None:
    user = UserCreate(
        username="preethi",
        email="preethi@example.com",
        full_name="Preethi User",
        password="strong-password",
        is_private=False,
    )

    assert user.username == "preethi"
    assert user.email == "preethi@example.com"


@pytest.mark.parametrize(
    "data",
    [
        {"caption": "", "image_file": "post.jpg"},
        {"caption": "x" * 101, "image_file": "post.jpg"},
    ],
)
def test_post_create_rejects_invalid_fields(data: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        PostCreate(**data)


@pytest.mark.parametrize("status", ["accepted", "rejected"])
def test_follow_request_accepts_supported_status(status: str) -> None:
    assert FollowRequestUpdate(status=status).status == status


def test_follow_request_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        FollowRequestUpdate(status="pending")
