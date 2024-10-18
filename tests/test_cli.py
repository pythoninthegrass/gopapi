#!/usr/bin/env python

import json
import os
import re
import sys
import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

from gopappy.cli import app, get_credentials, env_file_path

runner = CliRunner()

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('API_KEY', 'test_key')
    monkeypatch.setenv('API_SECRET', 'test_secret')
    monkeypatch.setenv('DOMAIN', 'test.com')

@pytest.fixture
def mock_get_env():
    with patch('gopappy.cli.get_env') as mock:
        mock.return_value = ('test_key', 'test_secret', 'test.com')
        yield mock

@pytest.fixture
def mock_get_keyring():
    with patch('gopappy.cli.get_keyring') as mock:
        mock.return_value = None
        yield mock

@pytest.fixture
def mock_get_credentials():
    with patch('gopappy.cli.get_credentials') as mock:
        mock.return_value = ('test_key', 'test_secret', 'test.com')
        yield mock

@pytest.fixture
def mock_api():
    with patch('gopappy.cli.API') as mock:
        yield mock.return_value

def test_get_credentials(mock_get_env, mock_get_keyring, tmp_path):
    mock_cwd = tmp_path / "gopappy"
    mock_cwd.mkdir()
    env_file = mock_cwd / ".env"
    env_file.touch()

    with patch('gopappy.cli.env_file_path', new=None):
        with patch('gopappy.cli.Path.cwd', return_value=mock_cwd):
            api_key, api_secret, domain = get_credentials()
            assert api_key == 'test_key'
            assert api_secret == 'test_secret'
            assert domain == 'test.com'
            mock_get_env.assert_called_once_with(str(env_file))
            mock_get_keyring.assert_not_called()

def test_get_credentials_with_env_file(mock_get_env, mock_get_keyring, tmp_path):
    env_file = tmp_path / "custom.env"
    env_file.touch()

    with patch('gopappy.cli.env_file_path', new=str(env_file)):
        api_key, api_secret, domain = get_credentials()
        assert api_key == 'test_key'
        assert api_secret == 'test_secret'
        assert domain == 'test.com'
        mock_get_env.assert_called_once_with(str(env_file))
        mock_get_keyring.assert_not_called()

def test_get_credentials_no_env_file(mock_get_env, mock_get_keyring, tmp_path):
    mock_cwd = tmp_path / "gopappy"
    mock_cwd.mkdir()

    mock_prompt = MagicMock(side_effect=["test_key", "test_secret", "test.com"])

    # Set up mock_get_env to return None values
    mock_get_env.return_value = (None, None, None)

    with patch('gopappy.cli.env_file_path', new=None):
        with patch('gopappy.cli.Path.cwd', return_value=mock_cwd):
            api_key, api_secret, domain = get_credentials(prompt_func=mock_prompt)

    assert api_key == "test_key"
    assert api_secret == "test_secret"
    assert domain == "test.com"
    mock_get_env.assert_called_once_with(None)
    mock_get_keyring.assert_called_once()
    assert mock_prompt.call_count == 3

def test_records(mock_get_credentials, mock_api):
    mock_api.get.return_value.json.return_value = [
        {"type": "A", "name": "test", "data": "192.0.2.1"},
        {"type": "CNAME", "name": "www", "data": "example.com"},
    ]
    result = runner.invoke(app, ["records", "example.com"])
    assert result.exit_code == 0
    assert "Domain: example.com" in result.output
    assert re.search(r"A\s+test\s+192\.0\.2\.1", result.output) is not None
    assert re.search(r"CNAME\s+www\s+example\.com", result.output) is not None

def test_records_with_type_filter(mock_get_credentials, mock_api):
    mock_api.get.return_value.json.return_value = [
        {"type": "A", "name": "test", "data": "192.0.2.1"},
        {"type": "CNAME", "name": "www", "data": "example.com"},
    ]
    result = runner.invoke(app, ["records", "example.com", "--type", "A"])
    assert result.exit_code == 0
    assert re.search(r"A\s+test\s+192\.0\.2\.1", result.output) is not None
    assert "CNAME" not in result.output

def test_add_record(mock_get_credentials, mock_api):
    mock_api.patch.return_value.status_code = 200
    result = runner.invoke(app, ["add-record", "example.com", "--type", "A", "--name", "test", "--data", "192.0.2.1"])
    assert result.exit_code == 0
    assert "Record added successfully." in result.output
    mock_api.patch.assert_called_once_with(
        "domains/example.com/records",
        json=[{"type": "A", "name": "test", "data": "192.0.2.1"}]
    )

def test_add_record_error(mock_get_credentials, mock_api):
    mock_api.patch.return_value.status_code = 400
    mock_api.patch.return_value.json.return_value = {"code": "INVALID_INPUT", "message": "Invalid input"}
    result = runner.invoke(app, ["add-record", "example.com", "--type", "A", "--name", "test", "--data", "invalid"])
    assert result.exit_code == 1
    assert "INVALID_INPUT" in result.output

@pytest.mark.parametrize("status_code, response_text, expected_output, expected_exit_code", [
    (200, "", "Record deleted successfully.\n", 0),
    (204, "", "Record deleted successfully.\n", 0),
    (404, '{"code":"NOT_FOUND","message":"Record not found"}', "Error: NOT_FOUND\nMessage: Record not found\n", 1),
])
def test_delete_record(mock_get_credentials, mock_api, status_code, response_text, expected_output, expected_exit_code):
    mock_api.delete.return_value.status_code = status_code
    mock_api.delete.return_value.text = response_text
    if response_text:
        mock_api.delete.return_value.json.return_value = json.loads(response_text)

    result = runner.invoke(app, ["delete-record", "example.com", "--type", "A", "--name", "test"], input="y\n")

    assert result.exit_code == expected_exit_code
    assert expected_output in result.output
    mock_api.delete.assert_called_once_with("domains/example.com/records/A/test")

def test_domains(mock_get_credentials, mock_api):
    mock_api.get.return_value.json.return_value = [
        {"domain": "example.com", "status": "ACTIVE"},
        {"domain": "example.org", "status": "INACTIVE"},
    ]
    result = runner.invoke(app, ["domains", "--status", ""])
    assert result.exit_code == 0
    assert "example.com" in result.output
    assert "ACTIVE" in result.output
    assert "example.org" in result.output
    assert "INACTIVE" in result.output

def test_domains_with_status_filter(mock_get_credentials, mock_api):
    mock_api.get.return_value.json.return_value = [
        {"domain": "example.com", "status": "ACTIVE"},
        {"domain": "example.org", "status": "INACTIVE"},
    ]
    result = runner.invoke(app, ["domains", "--status", "active"])
    assert result.exit_code == 0
    assert "example.com" in result.output
    assert "ACTIVE" in result.output
    assert "example.org" not in result.output

def test_check_availability(mock_get_credentials, mock_api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"available": True, "price": 10.99}
    mock_api.get.return_value = mock_response

    result = runner.invoke(app, ["check", "example.com"])

    assert result.exit_code == 0
    assert '"available": true' in result.output
    assert '"price": 10.99' in result.output
    mock_api.get.assert_called_once_with("domains/available?domain=example.com")
