import json

from async_captcha import app


def test_request_example_empty() -> None:
    response = app.test_client().post(
        "/contact", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json == {
        "email": ["key missing"],
        "message": ["key missing"],
        "captcha": ["key missing"],
    }


def test_request_example_bad_vals() -> None:
    response = app.test_client().post(
        "/contact",
        data=json.dumps(
            {
                "email": "invalidemail",
                "message": "short",
                "captcha": {"seed": "0123456789abcdef", "response": "invalid:("},
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json == {
        "email": ["expected a valid email address"],
        "message": ["minimum allowed length is 10"],
        "captcha": {"response": "bad captcha response"},
    }


def test_request_example_successful() -> None:
    response = app.test_client().post(
        "/contact",
        data=json.dumps(
            {
                "email": "abc@xyz.com",
                "message": "long enough message",
                "captcha": {"seed": "0123456789abcdef", "response": "fedcba9876543210"},
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json == {"success": True}
