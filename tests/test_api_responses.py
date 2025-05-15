from unittest.mock import patch

import pytest


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


@pytest.mark.skip(reason="Now is more than 500kb")
@pytest.mark.upload_file
def test_if_accept_files_bigger_than_500kb(client_fastapi):
    with open("tests/imgs/big.png", "rb") as f:
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
