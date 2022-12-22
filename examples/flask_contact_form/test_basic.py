import json

from basic import app


def test_request_example_empty() -> None:
    response = app.test_client().post(
        "/contact", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 400
    assert response.json == {
        "email": ["key missing"],
        "message": ["key missing"],
        "name": ["key missing"],
    }


def test_request_example_bad_vals() -> None:
    response = app.test_client().post(
        "/contact",
        data=json.dumps({"email": "invalidemail", "message": 5, "name": 3.14}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json == {
        "email": ["expected a valid email address"],
        "message": ["expected a string"],
        "name": ["expected a string"],
    }


def test_request_example_successful() -> None:
    for valid_dict in [
        {"email": "abc@def.com", "message": "something cool", "name": "bob"},
        {
            "email": "abc@def.com",
            "message": "something cool",
            "name": "bob",
            "subject": "my subject",
        },
    ]:
        response = app.test_client().post(
            "/contact",
            data=json.dumps(valid_dict),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json == {"success": True}
