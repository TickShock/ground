import pytest
import json
from tickshock.ground._common import get_env, to_dict
from tickshock.ground.exceptions import TickShockException


@pytest.mark.parametrize("key, value", [
    ("TEST_VAR", "hello_world"),
    ("EMPTY_VAR", ""),
    ("NUMERIC_VAR", "12345"),
])
def test_get_env_success(monkeypatch, key, value):
    """Verify get_env returns the correct string when the key exists."""
    monkeypatch.setenv(key, value)
    assert get_env(key) == value


def test_get_env_raises_exception(monkeypatch):
    """Verify get_env raises TickShockException when the key is missing."""
    monkeypatch.delenv("NON_EXISTENT_KEY", raising=False)
    with pytest.raises(TickShockException, match="env-var 'NON_EXISTENT_KEY' not found"):
        get_env("NON_EXISTENT_KEY")


@pytest.mark.parametrize("json_input, expected_output", [
    ('{"key": "value"}', {"key": "value"}),
    ('{"a": 1, "b": [1, 2]}', {"a": 1, "b": [1, 2]}),
    ('{}', {}),
])
def test_to_dict_success(json_input, expected_output):
    assert to_dict(json_input) == expected_output


@pytest.mark.parametrize("invalid_input", [
    None,
    123,
    True,
])
def test_to_dict_type_error_handling(invalid_input):
    assert to_dict(invalid_input) == {}


def test_to_dict_json_decode_error():
    with pytest.raises(json.JSONDecodeError):
        to_dict('{"broken": "json"')
