from free_game_notifier.icons import icon_from_url


def test_steam_favicon(mock_request, configuration):
    """Make sure the default is working"""
    x = icon_from_url("https://store.steampowered.com/some/link/page.html")
    assert x == "https://store.steampowered.com/favicon.ico"


def test_steam_settings(mock_request, configuration):
    """Make sure settings override works"""
    x = icon_from_url("https://custom_steam.org")
    assert x == "https://custom.store.steampowered.com/favicon.ico"


def test_invalid_url(mock_request_raise, configuration):
    x = icon_from_url("https://xyz-asdf-123.edu/store/games/bingo.html")
    assert x is None


def test_default_ubisoft(mock_request, configuration):
    x = icon_from_url("https://store.ubi.com/us/game/some_game.html")
    assert x == "https://www.ubisoft.com/favicon.ico"
