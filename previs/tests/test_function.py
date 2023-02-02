import json
from pathlib import Path
from numpy import bool_

import pytest
from previs import load, save, survey, search
from previs.utils import sanitize_booleans

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "data"
small_survey_file = TEST_DATA_DIR / "small_survey.json"


@pytest.mark.parametrize(
    "filepath",
    [small_survey_file, small_survey_file.with_suffix(""), str(small_survey_file)],
)
def test_load_survey(filepath):
    s = load(filepath)
    assert isinstance(s, dict)


@pytest.mark.parametrize("dic", [{"a": bool_(True)}, {"a": {"b": bool_(True)}}])
def test_json_sanitizing(dic):
    with pytest.raises(TypeError):
        json.dumps(dic)
    json.dumps(sanitize_booleans(dic))


def test_overwrite(tmpdir):
    s = load(small_survey_file)

    target_file = Path(tmpdir.join("already_there.json"))
    target_file.touch()

    with pytest.raises(FileExistsError):
        save(s, target_file)

    save(s, target_file, overwrite=True)


@pytest.mark.parametrize("filepath", ["s0", "s1.json"])
def test_save_survey(tmpdir, filepath):
    s = load(small_survey_file)
    target_path = Path(tmpdir.join(filepath))
    savepath = save(s, target_path)

    assert savepath.is_file()

    # json validation
    with open(savepath, mode="rt") as ofile:
        json.load(ofile)


def test_search():
    test_target = "WR104"
    d = search(test_target)
    magL = d["Mag"]["magL"]
    distance = d["Gaia_dr2"]["Dkpc"]

    true_magL = -2.13
    true_distance = 4.0
    assert magL == pytest.approx(true_magL, 0.01)
    assert distance == pytest.approx(true_distance, 0.1)
    assert d["Guiding_star"]["VLTI"] == "Science star"


def test_survey():
    test_list_target = ["WR118", "WR104"]
    d = survey(test_list_target)
    magL = d[test_list_target[1]]["Mag"]["magL"]
    true_magL = -2.13
    assert len(d) == len(test_list_target)
    assert magL == pytest.approx(true_magL, 0.01)
