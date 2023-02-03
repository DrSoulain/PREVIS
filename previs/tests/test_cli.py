import pytest
from matplotlib import pyplot as plt

from previs._cli.main import main


@pytest.fixture()
def close_figures():
    plt.close("all")
    yield
    plt.close("all")


@pytest.mark.usefixtures("close_figures")
@pytest.mark.parametrize("target", ["WR104", "Altair", "HD109255"])
def test_search(target):
    ret = main(
        [
            "search",
            "--target",
            str(target),
        ]
    )
    assert plt.gcf().number == 2
    assert ret == 0


@pytest.mark.usefixtures("close_figures")
def test_failed_search():
    with pytest.warns(UserWarning):
        test_false_target = "unknown"
        with pytest.raises(ValueError, match=f"{test_false_target} not in Simbad!"):
            ret = main(
                [
                    "search",
                    "--target",
                    test_false_target,
                ]
            )
            assert ret == 2


@pytest.mark.usefixtures("close_figures")
def test_survey():
    ret = main(["survey", "--target", "WR104", "WR118"])
    assert plt.gcf().number == 1
    assert ret == 0
