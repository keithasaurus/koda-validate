from django.test import Client


def test_request_example_empty() -> None:
    response = Client().post("/contact", data={}, content_type="application/json")
    assert response.status_code == 400
    assert response.json() == {
        "email": ["key missing"],
        "message": ["key missing"],
        "name": ["key missing"],
    }


def test_request_example_bad_vals() -> None:
    response = Client().post(
        "/contact",
        data={"email": "invalidemail", "message": 5, "name": 3.14},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json() == {
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
        response = Client().post(
            "/contact",
            data=valid_dict,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}
