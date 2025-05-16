from unittest.mock import patch

import pytest


@pytest.mark.front
def test_if_front_works(client_fastapi):
    response = client_fastapi.get("/")
    assert response.status_code == 200


@pytest.mark.upload_file
def test_if_returns_success(client_fastapi):
    with open("tests/imgs/pep.jpg", "rb") as f:
        response = client_fastapi.post(
            "/upload-file", files={"file": (f.name, f, "image/png")}
        )
    assert response.status_code == 200
    assert response.json()["success"] == True


@pytest.mark.upload_file
def test_if_accept_only_jpg_or_png(client_fastapi):
    with open("tests/imgs/pep.txt", "rb") as f:
        response = client_fastapi.post(
            "/upload-file", files={"file": (f.name, f, "text/plain")}
        )
    assert response.status_code == 415
    assert response.json()["error_message"] == "Only accept .png or .jpg"


@pytest.mark.xfail(reason="Maybe File not found.")
@pytest.mark.upload_file
def test_if_accept_files_bigger_than_500kb(client_fastapi):
    with open("tests/imgs/video.mp4", "rb") as f:
        response = client_fastapi.post(
            "/upload-file", files={"file": (f.name, f, "image/png")}
        )
    assert response.status_code == 415
    assert "file size is bigger than" in response.json()["error_message"]


@pytest.mark.upload_file
def test_if_server_error(client_fastapi):
    with open("tests/imgs/pep.jpg", "rb") as f:
        with patch("code.app.remove") as mock_app:
            mock_app.side_effect = Exception(
                "Internal server error"
            )  # force an error in remove() function

            response = client_fastapi.post(
                "/upload-file", files={"file": (f.name, f, "image/png")}
            )

            assert response.status_code == 500
            assert response.json()["error_message"] == "Internal server error"


@pytest.mark.upload_file
def test_if_returns_validation_error(client_fastapi):
    with open("tests/imgs/pep.jpg", "rb") as f:
        response = client_fastapi.post(
            "/upload-file", files={"file2": (f.name, f, "image/png")}
        )
    assert response.status_code == 422
    assert response.json()["error_message"] == "Validation error - Field required."
