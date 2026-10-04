"""
The Host allow-list of the HTTP transport.

DNS-rebinding protection refuses any Host it does not know with
"Invalid Host header". Reaching the server by a DNS name, its IP or through a
reverse proxy must be possible once that name is configured.
"""

import pytest
from starlette.testclient import TestClient

from vibemk.server.cli import parse_arguments
from vibemk.server.server import CheckMKMCPServer

TOKEN = "s3cr3t-token-value-long-enough"


def _status(app, host: str) -> int:
    with TestClient(app, base_url=f"http://{host}") as client:
        response = client.post(
            "/mcp",
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
            json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
        )
    return response.status_code


@pytest.fixture(autouse=True)
def token(monkeypatch):
    monkeypatch.setenv("VIBEMK_HTTP_TOKEN", TOKEN)


def test_an_unknown_host_is_refused():
    app = CheckMKMCPServer().http_app(host="0.0.0.0")

    assert _status(app, "mcp.example.com:8765") == 421


def test_localhost_is_accepted():
    app = CheckMKMCPServer().http_app(host="0.0.0.0")

    assert _status(app, "localhost:8765") != 421


@pytest.mark.parametrize("host", ["mcp.example.com:8765", "mcp.example.com"])
def test_a_configured_host_is_accepted_on_any_port(host):
    app = CheckMKMCPServer().http_app(host="0.0.0.0", allowed_hosts=["mcp.example.com"])

    assert _status(app, host) != 421


def test_a_wildcard_disables_the_host_check():
    app = CheckMKMCPServer().http_app(host="0.0.0.0", allowed_hosts=["*"])

    assert _status(app, "anything.example:1234") != 421


def test_allowed_hosts_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("VIBEMK_HTTP_ALLOWED_HOSTS", " mcp.example.com , 10.0.0.5,")

    assert parse_arguments([]).allowed_hosts == ["mcp.example.com", "10.0.0.5"]


def test_allowed_hosts_from_the_command_line():
    assert parse_arguments(["--allowed-hosts", "a,b"]).allowed_hosts == ["a", "b"]
