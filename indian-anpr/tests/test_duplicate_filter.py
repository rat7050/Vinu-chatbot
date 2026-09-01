import time

from services.duplicate_filter import DuplicateFilter


def test_duplicate_suppression():
    duplicate_filter = DuplicateFilter(cooldown_seconds=1.0)
    plate = "DL01AB1234"

    assert duplicate_filter.should_save(plate) is True
    assert duplicate_filter.should_save(plate) is False

    time.sleep(1.1)
    assert duplicate_filter.should_save(plate) is True
