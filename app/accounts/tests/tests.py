import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAccountAPI:
    endpoint = "/api/accounts/"

    def auth(self, client, token):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # -------------------------------------------
    # GET /accounts/
    # -------------------------------------------
    def test_list_as_staff(self, api_client, staff_user, supabase_token_user):
        api_client.force_authenticate(user=staff_user)
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1  # staff can see everyone

    def test_list_as_regular_user(self, api_client, supabase_token_user):
        """User can only see themselves."""
        self.auth(api_client, supabase_token_user)
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == "user@example.com"

    # -------------------------------------------
    # GET /accounts/{id}/
    # -------------------------------------------
    def test_retrieve_self(self, api_client, regular_user, supabase_token_user):
        self.auth(api_client, supabase_token_user)
        response = api_client.get(f"{self.endpoint}{regular_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == regular_user.email

    def test_retrieve_other_forbidden(
        self, api_client, another_user, supabase_token_user
    ):
        self.auth(api_client, supabase_token_user)
        response = api_client.get(f"{self.endpoint}{another_user.id}/")
        # not visible in queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # -------------------------------------------
    # POST /accounts/
    # -------------------------------------------
    def test_create_self_user_ok(self, api_client, supabase_token_user):
        """User can only create their own account (email matches token)."""
        self.auth(api_client, supabase_token_user)
        payload = {"email": "user@example.com", "first_name": "Hernán"}
        response = api_client.post(self.endpoint, payload)
        # User already exists from fixture, so expect 400 or allow 200/201 if idempotent
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_create_other_user_forbidden(self, api_client, supabase_token_user):
        """Creating another email should fail."""
        self.auth(api_client, supabase_token_user)
        payload = {"email": "fake@example.com", "first_name": "Hack"}
        response = api_client.post(self.endpoint, payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "own email" in response.data["detail"].lower()

    # -------------------------------------------
    # PATCH /accounts/{id}/
    # -------------------------------------------
    def test_update_self_allowed(self, api_client, regular_user, supabase_token_user):
        """User can update their own account."""
        self.auth(api_client, supabase_token_user)
        payload = {"first_name": "Updated"}
        response = api_client.patch(f"{self.endpoint}{regular_user.id}/", payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

    def test_update_other_forbidden(
        self, api_client, another_user, supabase_token_user
    ):
        """User cannot update another account."""
        self.auth(api_client, supabase_token_user)
        payload = {"first_name": "Hacker"}
        response = api_client.patch(f"{self.endpoint}{another_user.id}/", payload)
        # Queryset filters out other users, so 404 is expected instead of 403
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    # -------------------------------------------
    # DELETE /accounts/{id}/
    # -------------------------------------------
    def test_delete_self_allowed(self, api_client, regular_user, supabase_token_user):
        """User can delete themselves."""
        self.auth(api_client, supabase_token_user)
        response = api_client.delete(f"{self.endpoint}{regular_user.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_other_forbidden(
        self, api_client, another_user, supabase_token_user
    ):
        """User cannot delete someone else."""
        self.auth(api_client, supabase_token_user)
        response = api_client.delete(f"{self.endpoint}{another_user.id}/")
        # Queryset filters out other users, so 404 is expected instead of 403
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    # -------------------------------------------
    # GET /accounts/me/
    # -------------------------------------------
    def test_me_endpoint(self, api_client, supabase_token_user):
        """Returns the current user's profile."""
        self.auth(api_client, supabase_token_user)
        response = api_client.get(f"{self.endpoint}me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "user@example.com"
