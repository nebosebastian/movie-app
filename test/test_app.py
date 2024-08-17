import pytest
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db


# Create an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

def test_signup(client):
    response = client.post("/signup", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "email" in data  # Removed assertion for 'id' since it's not returned

def test_login(client):
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_create_movie(client):
    token = test_login(client)
    response = client.post("/movie/", json={
        "title": "Inception",
        "author": "Christopher Nolan",
        "release_date": "2010-07-16",
        "created_by": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Inception"
    assert data["author"] == "Christopher Nolan"
    assert "id" in data
    return data["id"]

def test_update_movie(client):
    token = test_login(client)
    movie_id = test_create_movie(client)  # Create a movie to update
    response = client.put(f"/movies/{movie_id}", json={
        "title": "Inception Updated",
        "author": "Christopher Nolan",
        "release_date": "2010-07-16",
        "created_by": 1
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Inception Updated"
    assert data["author"] == "Christopher Nolan"

def test_delete_movie(client):
    # Log in to get a token
    token = test_login(client)

    # Create a movie to delete
    movie_id = test_create_movie(client)
    
    # Perform the deletion
    response = client.delete(f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    
    # Verify that the response contains the correct movie data
    assert data["id"] == movie_id
    assert data["title"] == "Inception"
    assert data["author"] == "Christopher Nolan"

    # Try to get the deleted movie
    response = client.get(f"/movie/{movie_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}


def test_get_movies(client):
    token = test_login(client)
    
    # Create a few movies to test retrieval
    movie_ids = []
    for i in range(3):
        response = client.post("/movie/", json={
            "title": f"Movie {i}",
            "author": "Author",
            "release_date": "2020-01-01",
            "created_by": 1
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        movie_ids.append(data["id"])

    # Test retrieval of all movies
    response = client.get("/movies/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # Ensure at least the number of movies created are present

    # Check that all created movies are in the response
    response_titles = [movie["title"] for movie in data]
    for i in range(3):
        assert f"Movie {i}" in response_titles

def test_post_rating(client):
    token = test_login(client)

    # Create a movie to rate
    movie_id = test_create_movie(client)

    # Post a rating
    response = client.post("/ratings/", json={
        "movie_id": movie_id,
        "rating": 5
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["rating"] == 5

def test_get_ratings(client):
    token = test_login(client)
    
    # Create a movie to rate
    movie_id = test_create_movie(client)
    
    # Create a rating
    client.post("/ratings/", json={
        "movie_id": movie_id,
        "rating": 5
    }, headers={"Authorization": f"Bearer {token}"})

    # Retrieve ratings without filters
    response = client.get("/ratings/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Ensure that there is at least one rating

    # Retrieve ratings by movie_id
    response = client.get(f"/ratings/?movie_id={movie_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(rating["movie_id"] == movie_id for rating in data)

def test_post_comment(client):
    token = test_login(client)
    movie_id = test_create_movie(client)

    response = client.post("/comments/", json={
        "movie_id": movie_id,
        "comment": "Great movie!"
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == movie_id
    assert data["comment"] == "Great movie!"
    assert "user_id" in data


def test_get_comments(client):
    token = test_login(client)
    movie_id = test_create_movie(client)

    # Post a comment
    client.post("/comments/", json={"movie_id": movie_id, "comment": "Great movie!"}, headers={"Authorization": f"Bearer {token}"})

    # Retrieve comments without filters
    response = client.get("/comments/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) > 0

    # Retrieve comments by movie_id
    response = client.get(f"/comments/?movie_id={movie_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) > 0
    assert all(comment["movie_id"] == movie_id for comment in data)
