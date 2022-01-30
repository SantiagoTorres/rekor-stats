"""Tests for rekor-stats"""

from query import detect_filenames, fetch_record


def test_detect_filenames():
    """Test detect_filenames() function."""
    assert detect_filenames(height=4, basename="test_data_folder") == set([0, 2])


def test_fetch_record():
    """Test detect_filenames() function."""
    # this test depends on the rekor log NOT being reset and checks that
    # second element of the record at index 5 has a length of 33, a way
    # of doing a precise but admittedly arbitrary test. Better tests welcome!
    assert len(fetch_record(index=5, basename="test_data_folder")[1]) == 33
