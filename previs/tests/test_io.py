from pathlib import Path
import tempfile
import json

import pytest
from previs import survey, save_survey, load_survey

TEST_DATA_DIR = Path(__file__).parent / "data"
ARTIFACTS_DIR = TEST_DATA_DIR / ".artifacts"
small_survey_file = TEST_DATA_DIR / "small_survey.json"
small_survey_sans_ext = small_survey_file.with_suffix('')


@pytest.mark.parametrize(
    "filepath", [small_survey_file, small_survey_sans_ext, str(small_survey_file)]
)
def test_load_survey(filepath):
    s = load_survey(filepath)
    assert isinstance(s, dict)


def test_reproduce_survey():
    s1 = load_survey(small_survey_file)
    stars = list(s.keys())

    s2 = survey(stars)
    # assert s1 == s2


def test_overwrite():
    s = load_survey(small_survey_file)

    target_file = ARTIFACTS_DIR / "dont_touch_me.json"
    with open(target_file, "wt") as ofile:
        ofile.write("")

    with pytest.raises(FileExistsError):
        save_survey(s, target_file)

    save_survey(s, target_file, overwrite=True)


@pytest.mark.parametrize("filepath", ["s0", "s1.json"])
def test_save_survey(filepath):
    s = load_survey(small_survey_file)
    save_survey(s, ARTIFACTS_DIR / filepath)
    assert Path(filepath).is_file()

    # json validation
    with open(filepath, mode="rt") as ofile:
        d = json.load(ofile)
