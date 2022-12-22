import json

from basic import app


def test_request_example_empty() -> None:
    response = app.test_client().post(
        "/contact", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json == {"email": ["key missing"], "message": ["key missing"]}


def test_request_example_bad_vals() -> None:
    response = app.test_client().post(
        "/contact",
        data=json.dumps({"email": "invalidemail", "message": "short"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json == {
        "email": ["expected a valid email address"],
        "message": ["minimum allowed length is 10"],
    }


def test_request_example_successful() -> None:
    response = app.test_client().post(
        "/contact",
        data=json.dumps({"email": "abc@def.com", "message": "something cool"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json == {"success": True}
