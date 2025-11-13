import pytest
from fastapi.testclient import TestClient
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import main  

# --- Test Setup ---

@pytest.fixture(scope="function")
def client(tmp_path, monkeypatch):
    """
    Pytest fixture to set up a TestClient with a temporary storage directory.
    This fixture runs once per test function.
    """
    # Create a temporary storage directory for this test
    test_storage_dir = tmp_path / "test_storage"
    test_storage_dir.mkdir()

    # Use monkeypatch to override the global STORAGE_DIR in the main app
    monkeypatch.setattr(main, "STORAGE_DIR", test_storage_dir)

    # Reset the file counter for each test
    monkeypatch.setattr(main, "files_stored_counter", 0)
    
    # Re-initialize the counter function if necessary (though resetting the var is key)
    monkeypatch.setattr(main, "get_file_count", lambda: 0)


    # Create the TestClient instance using the app
    with TestClient(main.app) as test_client:
        yield test_client
    
    # Cleanup is handled by tmp_path fixture automatically

# --- Tests ---

def test_root_endpoint(client):
    """Test the root (/) endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File Storage API"
    assert "/files" in [ep.split(" ")[-1] for ep in data["endpoints"]]

def test_health_check_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_list_files_empty(client):
    """Test listing files when storage is empty."""
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert data["files"] == []
    assert data["count"] == 0

def test_store_file_success(client):
    """Test successfully storing a new file."""
    file_content = b"This is a test file."
    file_name = "test_file.txt"

    response = client.post(
        "/files",
        files={"file": (file_name, file_content, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File stored successfully"
    assert data["filename"] == file_name
    assert data["size"] == len(file_content)

    # Verify file exists in the (mocked) storage
    storage_dir = main.STORAGE_DIR
    expected_file_path = storage_dir / file_name
    assert expected_file_path.exists()
    assert expected_file_path.read_bytes() == file_content

def test_get_file_success(client):
    """Test retrieving a file that exists."""
    file_content = b"Hello, world!"
    file_name = "hello.txt"
    
    # First, create the file in storage (bypassing POST for a direct setup)
    storage_dir = main.STORAGE_DIR
    (storage_dir / file_name).write_bytes(file_content)

    # Now, test the GET endpoint
    response = client.get(f"/files/{file_name}")
    
    assert response.status_code == 200
    assert response.content == file_content
    assert response.headers["content-disposition"] == f'attachment; filename="{file_name}"'

def test_get_file_not_found(client):
    """Test retrieving a file that does not exist."""
    response = client.get("/files/non_existent_file.log")
    assert response.status_code == 404
    assert response.json()["detail"] == "File 'non_existent_file.log' not found"


def test_metrics_and_file_counting(client):
    """Test the /metrics endpoint and its counters."""
    # 1. Check initial metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["files_stored_total"] == 0
    assert data["files_current"] == 0
    assert data["total_storage_bytes"] == 0

    # 2. Store one file
    file_content_1 = b"file one"
    client.post("/files", files={"file": ("file1.txt", file_content_1)})

    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["files_stored_total"] == 1
    assert data["files_current"] == 1
    assert data["total_storage_bytes"] == len(file_content_1)

    # 3. Store a second file
    file_content_2 = b"file two content"
    client.post("/files", files={"file": ("file2.log", file_content_2)})

    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["files_stored_total"] == 2
    assert data["files_current"] == 2
    assert data["total_storage_bytes"] == len(file_content_1) + len(file_content_2)

    # 4. Overwrite the first file
    file_content_1_new = b"new file one content"
    client.post("/files", files={"file": ("file1.txt", file_content_1_new)})
    
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    # files_stored_total should NOT increment on overwrite
    assert data["files_stored_total"] == 2 
    assert data["files_current"] == 2
    assert data["total_storage_bytes"] == len(file_content_1_new) + len(file_content_2)