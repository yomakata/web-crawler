"""Unit tests for API endpoints"""
import pytest
import json
from api.app import create_app
from api.models import job_store


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_index_endpoint(client):
    """Test index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'name' in data
    assert 'version' in data


def test_api_docs(client):
    """Test API documentation endpoint"""
    response = client.get('/api/docs')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'endpoints' in data


def test_crawl_single_no_body(client):
    """Test single crawl without request body"""
    response = client.post('/api/crawl/single')
    assert response.status_code == 400


def test_crawl_single_invalid_url(client):
    """Test single crawl with invalid URL"""
    response = client.post(
        '/api/crawl/single',
        data=json.dumps({'url': 'invalid-url'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_get_job_status_not_found(client):
    """Test getting status of non-existent job"""
    response = client.get('/api/job/nonexistent/status')
    assert response.status_code == 404


def test_get_history(client):
    """Test getting crawl history"""
    response = client.get('/api/history')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'history' in data
    assert 'total' in data
