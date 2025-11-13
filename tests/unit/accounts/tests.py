import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAccountAPI:
    endpoint = "/api/accounts/"

    # -------------------------------------------
    # GET /accounts/
    # -------------------------------------------
    def test_list_as_regular_user_allowed(self, api_client, regular_user, another_user):
        """Regular user can list accounts but only sees their own account."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == regular_user.email

    def test_list_as_staff_allowed(
        self, api_client, staff_user, regular_user, another_user
    ):
        """Staff user can list all accounts and sees everyone."""
        api_client.force_authenticate(user=staff_user)
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert (
            len(response.data) >= 3
        )  # staff can see everyone (staff + regular + another)

    # -------------------------------------------
    # GET /accounts/{id}/
    # -------------------------------------------
    def test_retrieve_self_allowed(self, api_client, regular_user):
        """Regular user can retrieve their own account details."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get(f"{self.endpoint}{regular_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == regular_user.email

    def test_retrieve_other_forbidden(self, api_client, regular_user, another_user):
        """Regular user cannot retrieve another user's account details."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get(f"{self.endpoint}{another_user.id}/")
        # not visible in queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_other_as_staff_allowed(
        self, api_client, staff_user, another_user
    ):
        """Staff user can retrieve any user's account details."""
        api_client.force_authenticate(user=staff_user)
        response = api_client.get(f"{self.endpoint}{another_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == another_user.email

    # -------------------------------------------
    # POST /accounts/
    # -------------------------------------------

    def test_create_self_user_not_in_db_allowed(self, api_client, not_in_db_user):
        """User can create their own account when it doesn't exist in the database."""
        api_client.force_authenticate(user=not_in_db_user)
        payload = {
            "email": not_in_db_user.email,
            "first_name": not_in_db_user.first_name,
        }
        response = api_client.post(self.endpoint, payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_self_user_already_in_db_bad_request(self, api_client, regular_user):
        """User cannot create their own account if it already exists in the database."""
        api_client.force_authenticate(user=regular_user)
        payload = {"email": regular_user.email, "first_name": regular_user.first_name}
        response = api_client.post(self.endpoint, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_other_user_forbidden(self, api_client, regular_user):
        """Regular user cannot create an account for another user."""
        api_client.force_authenticate(user=regular_user)
        payload = {"email": "fake@example.com", "first_name": "Hack"}
        response = api_client.post(self.endpoint, payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "own email" in response.data["detail"].lower()

    def test_create_other_user_as_staff_allowed(self, api_client, staff_user):
        """Staff user can create an account for another user."""
        api_client.force_authenticate(user=staff_user)
        payload = {"email": "fake@example.com", "first_name": "Hack"}
        response = api_client.post(self.endpoint, payload)
        assert response.status_code == status.HTTP_201_CREATED

    # -------------------------------------------
    # PATCH /accounts/{id}/
    # -------------------------------------------
    def test_update_self_allowed(self, api_client, regular_user):
        """Regular user can update their own account."""
        api_client.force_authenticate(user=regular_user)
        payload = {"first_name": "Updated"}
        response = api_client.patch(f"{self.endpoint}{regular_user.id}/", payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

    def test_update_other_forbidden(self, api_client, regular_user, another_user):
        """Regular user cannot update another user's account."""
        api_client.force_authenticate(user=regular_user)
        payload = {"first_name": "Hacker"}
        response = api_client.patch(f"{self.endpoint}{another_user.id}/", payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_other_as_staff_allowed(self, api_client, staff_user, another_user):
        """Staff user can update another user's account."""
        api_client.force_authenticate(user=staff_user)
        payload = {"first_name": "Hacker"}
        response = api_client.patch(f"{self.endpoint}{another_user.id}/", payload)
        assert response.status_code == status.HTTP_200_OK

    # -------------------------------------------
    # DELETE /accounts/{id}/
    # -------------------------------------------
    def test_delete_self_allowed(self, api_client, regular_user):
        """Regular user can delete their own account."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.delete(f"{self.endpoint}{regular_user.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_other_forbidden(self, api_client, regular_user, another_user):
        """Regular user cannot delete another user's account."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.delete(f"{self.endpoint}{another_user.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_other_as_staff_allowed(self, api_client, staff_user, another_user):
        """Staff user can delete another user's account."""
        api_client.force_authenticate(user=staff_user)
        response = api_client.delete(f"{self.endpoint}{another_user.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # -------------------------------------------
    # GET /accounts/me/
    # -------------------------------------------
    def test_me_endpoint(self, api_client, regular_user):
        """User can retrieve their own profile via the /me endpoint."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get(f"{self.endpoint}me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "user@example.com"
