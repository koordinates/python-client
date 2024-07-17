import pytest
import responses
from koordinates import Client
from koordinates.exceptions import RedirectException


def test_redirect_handling():
    www_client = Client(token="test", host="www.test.koordinates.com")
    test_client = Client(token="test", host="test.koordinates.com")
    ID = 1474

    www_url = www_client.get_url("LAYER", "GET", "single", {"id": ID})
    test_url = test_client.get_url("LAYER", "GET", "single", {"id": ID})

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            www_url,
            status=302,
            adding_headers={"Location": test_url},
        )

        with pytest.raises(RedirectException) as e:
            layer = www_client.layers.get(ID)

        assert e.value.args == (
            "Server responded with redirect (302 https://test.koordinates.com/services/api/v1/layers/1474/)",
        )
