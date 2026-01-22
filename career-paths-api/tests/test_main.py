"""
Tests for main application.
"""


def test_root_endpoint(client):
    """Test: Root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "version" in data


def test_health_check(client):
    """Test: Health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
