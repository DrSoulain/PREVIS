from pathlib import Path
import tempfile
import json

import pytest
from previs import survey, save_survey, load_survey

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "data"
small_survey_file = TEST_DATA_DIR / "small_survey.json"
small_survey_sans_ext = small_survey_file.with_suffix("")


@pytest.mark.parametrize(
    "filepath", [small_survey_file, small_survey_sans_ext, str(small_survey_file)]
)
def test_load_survey(filepath):
    s = load_survey(filepath)
    assert isinstance(s, dict)


def test_reproduce_survey():
    s1 = load_survey(small_survey_file)
    stars = list(s1.keys())

    s2 = survey(stars)
    assert isinstance(s2, dict)
    assert len(s1) == len(s2)
    for star in s1:
        assert star in s2
        assert set(list(s1[star].keys())) == set(list(s2[star].keys()))


def test_overwrite(tmpdir):
    s = load_survey(small_survey_file)

    target_file = Path(tmpdir.join("already_there.json"))
    target_file.touch()

    with pytest.raises(FileExistsError):
        save_survey(s, target_file)

    save_survey(s, target_file, overwrite=True)


@pytest.mark.parametrize("filepath", ["s0", "s1.json"])
def test_save_survey(tmpdir, filepath):
    s = load_survey(small_survey_file)
    savefile = Path(tmpdir.join(filepath))
    savepath = save_survey(s, savefile)

    assert savepath.is_file()
    # json validation
    with open(savepath, mode="rt") as ofile:
        d = json.load(ofile)
