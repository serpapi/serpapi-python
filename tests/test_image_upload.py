from io import BytesIO, StringIO
from unittest.mock import Mock

import httpx
import pytest

import serpapi


def json_response(data):
    request = httpx.Request("POST", "https://serpapi.com/image")
    return httpx.Response(200, content=data, request=request)


def test_upload_image_path_sends_multipart_request(tmp_path):
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"fake-png-data")
    client = serpapi.Client(api_key="test-api-key")

    def request(**kwargs):
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "https://serpapi.com/image"
        assert kwargs["params"] == {}
        assert kwargs["data"] == {"api_key": "test-api-key"}
        assert kwargs["files"]["image"].name == str(image_path)
        assert kwargs["files"]["image"].read() == b"fake-png-data"
        return json_response(
            b'{"message": "Image uploaded successfully.", "image_id": "image-123"}'
        )

    client.session.request = Mock(side_effect=request)

    result = client.upload_image(image_path)

    assert result["image_id"] == "image-123"


def test_upload_image_accepts_open_binary_file_and_request_options():
    image = BytesIO(b"fake-image-data")
    client = serpapi.Client(api_key="client-api-key", timeout=10)
    client.session.request = Mock(
        return_value=json_response(b'{"image_id": "image-456"}')
    )

    result = client.upload_image(
        image,
        api_key="request-api-key",
        timeout=5,
        zero_trace="true",
    )

    assert result == {"image_id": "image-456"}
    assert not image.closed
    request_kwargs = client.session.request.call_args.kwargs
    assert request_kwargs["params"] == {}
    assert request_kwargs["data"] == {
        "api_key": "request-api-key",
        "zero_trace": "true",
    }
    assert request_kwargs["files"] == {"image": image}
    assert request_kwargs["timeout"] == 5


def test_upload_image_rejects_text_mode_file(tmp_path):
    image_path = tmp_path / "test.png"
    image_path.write_text("not binary image data")
    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock()

    with image_path.open("r") as image, pytest.raises(
        TypeError, match="opened in binary mode"
    ):
        client.upload_image(image)

    client.session.request.assert_not_called()


def test_upload_image_rejects_string_io():
    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock()

    with pytest.raises(TypeError, match="opened in binary mode"):
        client.upload_image(StringIO("not binary image data"))

    client.session.request.assert_not_called()


def test_request_injects_api_key_when_form_data_does_not_include_it():
    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock(return_value=json_response(b"{}"))

    client.request("POST", "/example", params={}, data={"field": "value"})

    request_kwargs = client.session.request.call_args.kwargs
    assert request_kwargs["params"] == {"api_key": "test-api-key"}
    assert request_kwargs["data"] == {"field": "value"}


def test_module_exposes_upload_image_entrypoint():
    assert callable(serpapi.upload_image)
