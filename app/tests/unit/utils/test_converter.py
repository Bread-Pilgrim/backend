import datetime

import pytest

from app.utils.converter import operating_hours_to_open_status


def test_operating_hours_to_open_status_day_off():
    is_opened = False
    close_time = None
    open_time = None

    assert operating_hours_to_open_status(is_opened, close_time, open_time) == "D"


def test_operating_hours_to_open_status_open_with_time():
    is_opened = True
    close_time = datetime.time(23, 40, 00)
    open_time = datetime.time(9, 00, 00)

    assert operating_hours_to_open_status(is_opened, close_time, open_time) == "O"


def test_operating_hours_to_open_status_open_without_time():
    is_opened = True
    close_time = None
    open_time = None

    assert operating_hours_to_open_status(is_opened, close_time, open_time) == "O"


def test_operating_hours_to_open_status_close():
    is_opened = True
    close_time = datetime.time(11, 40, 00)
    open_time = datetime.time(9, 00, 00)

    assert operating_hours_to_open_status(is_opened, close_time, open_time) == "C"
