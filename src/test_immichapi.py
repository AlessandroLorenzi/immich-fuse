from .immich_api import ImmichApi


def test_immich_api():
    api = ImmichApi()
    assert api is not None, "ImmichApi instance should not be None"


def test_get_asset_stats():
    api = ImmichApi()
    stats = api.get_asset_stats("2c875c19-cfb0-4ace-99aa-e25df12ca61d")
    assert stats is not None, "Asset stats should not be None"
    assert "id" in stats, "Asset stats should contain 'id'"


def test_get_asset():
    api = ImmichApi()
    asset = api.get_asset("2c875c19-cfb0-4ace-99aa-e25df12ca61d")
    assert asset is not None, "Asset should not be None"
