import json
from pathlib import Path
from numpy import bool_

import pytest
from previs import load, save, survey
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


@pytest.mark.timeout(120)
def test_reproduce_survey():
    s1 = load(small_survey_file)
    stars = list(s1.keys())

    s2 = survey(stars)
    assert isinstance(s2, dict)
    assert len(s1) == len(s2)
    for star in s1:
        assert star in s2
        assert set(list(s1[star].keys())) == set(list(s2[star].keys()))


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
