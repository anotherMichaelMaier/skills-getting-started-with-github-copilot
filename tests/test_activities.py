"""Tests for the Mergington High School Activities API."""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Check that we have the expected number of activities
        assert len(data) == 9

        # Check that Chess Club exists and has correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

        # Check that Programming Class exists and has participants
        assert "Programming Class" in data
        prog_class = data["Programming Class"]
        assert len(prog_class["participants"]) == 2
        assert "emma@mergington.edu" in prog_class["participants"]


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up test@mergington.edu for Chess Club" in data["message"]

        # Verify the participant was added by checking the activities list
        response = client.get("/activities")
        activities = response.json()
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404."""
        response = client.post("/activities/NonExistent%20Activity/signup?email=test@mergington.edu")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered(self, client):
        """Test signup when student is already registered returns 400."""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")

        # Try to signup again
        response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" in data["detail"]


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # First register a student
        client.post("/activities/Chess%20Club/signup?email=unregister_test@mergington.edu")

        # Now unregister
        response = client.delete("/activities/Chess%20Club/unregister?email=unregister_test@mergington.edu")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered unregister_test@mergington.edu from Chess Club" in data["message"]

        # Verify the participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "unregister_test@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@mergington.edu")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered returns 400."""
        response = client.delete("/activities/Chess%20Club/unregister?email=not_registered@mergington.edu")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is not signed up for this activity" in data["detail"]


class TestRootEndpoint:
    """Test cases for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"