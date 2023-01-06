import pytest
from django.test import AsyncClient  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_request_example_empty() -> None:
    response = await AsyncClient().post(
        "/contact-async", data={}, content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json() == {
        "email": ["key missing"],
        "message": ["key missing"],
        "captcha": ["key missing"],
    }


@pytest.mark.asyncio
async def test_request_example_bad_vals() -> None:
    response = await AsyncClient().post(
        "/contact-async",
        data={
            "email": "invalidemail",
            "message": "short",
            "captcha": {"seed": "0123456789abcdef", "response": "invalid:("},
        },
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json() == {
        "email": ["expected a valid email address"],
        "message": ["minimum allowed length is 10"],
        "captcha": {"response": "bad captcha response"},
    }


@pytest.mark.asyncio
async def test_request_example_successful() -> None:
    response = await AsyncClient().post(
        "/contact-async",
        data={
            "email": "abc@xyz.com",
            "message": "long enough message",
            "captcha": {"seed": "0123456789abcdef", "response": "fedcba9876543210"},
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}
