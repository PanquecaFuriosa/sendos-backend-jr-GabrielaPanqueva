"""
Tests para la aplicación principal.
"""


def test_root_endpoint(client):
    """Test: Endpoint raíz retorna información correcta."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "version" in data


def test_health_check(client):
    """Test: Health check endpoint funciona."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
