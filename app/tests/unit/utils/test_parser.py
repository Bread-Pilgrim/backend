import pytest

from app.utils.parser import parse_comma_to_list


def test_parse_comma_to_list_basic():
    assert parse_comma_to_list("A,B,C") == ["A", "B", "C"]


def test_parse_comma_to_list_with_spaces():
    assert parse_comma_to_list(" A , B , C ") == ["A", "B", "C"]


def test_parse_comma_to_list_with_empty_values():
    assert parse_comma_to_list("A,,C, ,D") == ["A", "C", "D"]


def test_parse_comma_to_list_only_one():
    assert parse_comma_to_list("A,") == ["A"]
