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

from gopappy.cli import app

runner = CliRunner()

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('API_KEY', 'test_key')
    monkeypatch.setenv('API_SECRET', 'test_secret')
    monkeypatch.setenv('DOMAIN', 'test.com')

def test_auth(mock_env_vars):
    from gopappy.auth import get_env

    api_key, api_secret, domain = get_env()
    assert api_key == 'test_key'
    assert api_secret == 'test_secret'
    assert domain == 'test.com'

@pytest.fixture
def mock_api():
    with patch('gopappy.cli.API') as mock:
        yield mock.shared.return_value

def test_records(mock_api):
    mock_api.get.return_value.json.return_value = [
        {"type": "A", "name": "test", "data": "192.0.2.1"},
        {"type": "CNAME", "name": "www", "data": "example.com"},
    ]
    result = runner.invoke(app, ["records", "example.com"])
    assert result.exit_code == 0
    assert "Domain: example.com" in result.output

    assert "A" in result.output and "test" in result.output
    assert "CNAME" in result.output and "www" in result.output

    assert re.search(r"A\s+test\s+192\.0\.2\.1", result.output) is not None
    assert re.search(r"CNAME\s+www\s+example\.com", result.output) is not None

def test_records_with_type_filter(mock_api):
    mock_api.get.return_value.json.return_value = [
        {"type": "A", "name": "test", "data": "192.0.2.1"},
        {"type": "CNAME", "name": "www", "data": "example.com"},
    ]
    result = runner.invoke(app, ["records", "example.com", "--type", "A"])
    assert result.exit_code == 0
    assert re.search(r"A\s+test\s+192\.0\.2\.1", result.output) is not None
    assert "CNAME" not in result.output

def test_add_record(mock_api):
    mock_api.patch.return_value.status_code = 200
    result = runner.invoke(app, ["add-record", "example.com", "--type", "A", "--name", "test", "--data", "192.0.2.1"])
    assert result.exit_code == 0
    assert "Record added successfully." in result.output
    mock_api.patch.assert_called_once_with(
        "domains/example.com/records",
        json=[{"type": "A", "name": "test", "data": "192.0.2.1"}]
    )

def test_add_record_error(mock_api):
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
def test_delete_record(mock_api, status_code, response_text, expected_output, expected_exit_code):
    mock_api.delete.return_value.status_code = status_code
    mock_api.delete.return_value.text = response_text
    if response_text:
        mock_api.delete.return_value.json.return_value = json.loads(response_text)

    result = runner.invoke(app, ["delete-record", "example.com", "--type", "A", "--name", "test"], input="y\n")

    assert result.exit_code == expected_exit_code
    assert expected_output in result.output
    mock_api.delete.assert_called_once_with("domains/example.com/records/A/test")

def test_domains(mock_api):
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

def test_domains_default(mock_api):
    mock_api.get.return_value.json.return_value = [
        {"domain": "example.com", "status": "ACTIVE"},
        {"domain": "example.org", "status": "INACTIVE"},
    ]
    result = runner.invoke(app, ["domains"])
    assert result.exit_code == 0
    assert "example.com" in result.output
    assert "ACTIVE" in result.output
    assert "example.org" not in result.output
    assert "INACTIVE" not in result.output

def test_domains_with_status_filter(mock_api):
    mock_api.get.return_value.json.return_value = [
        {"domain": "example.com", "status": "ACTIVE"},
        {"domain": "example.org", "status": "INACTIVE"},
    ]
    result = runner.invoke(app, ["domains", "--status", "active"])
    assert result.exit_code == 0
    assert "example.com" in result.output
    assert "ACTIVE" in result.output
    assert "example.org" not in result.output

def test_check_availability(mock_api):
    mock_api.get.return_value.json.return_value = {"available": True, "price": 10.99}
    result = runner.invoke(app, ["check", "example.com"])
    assert result.exit_code == 0
    assert "{'available': True, 'price': 10.99}" in result.output

def test_version():
    import gopappy
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == gopappy.__version__

def test_main_with_no_arguments():
    with patch('sys.argv', ['gopappy']):
        with patch('gopappy.cli.app') as mock_app:
            from gopappy.cli import main
            main()
            mock_app.assert_called_once_with(['--help'])
