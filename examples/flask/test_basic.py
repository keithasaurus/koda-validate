from basic import app


def test_request_example():
    response = app.test_client().post("/contact", data={})
    assert response.status_code == 400

    # assert b"<h2>Hello, World!</h2>" in response.data
