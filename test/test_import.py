def test_import():
    import radiosoma
    from radiosoma import SomaFmStation


def test_version():
    from radiosoma.version import __version__
    assert __version__
