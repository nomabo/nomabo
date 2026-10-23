from nomabo import saluer, aire_cercle


def test_saluer():
    assert saluer("Marie") == "Bonjour, Marie !"


def test_aire_cercle():
    assert aire_cercle(0) == 0
