"""Integration tests for superadmin user management endpoints."""

import uuid

from fastapi.testclient import TestClient

from apps.api.src.api.v1.core.security import create_access_token, get_password_hash
from apps.api.src.api.v1.models.user import User


class TestUserManagementEndpoints:
    """Tests for GET/PATCH/DELETE /api/v1/users (superadmin only)."""

    def test_stats_requires_auth(self, client: TestClient):
        response = client.get("/api/v1/users/stats")
        assert response.status_code == 401

    def test_stats_forbidden_for_client_admin(self, client: TestClient, admin_auth_token: str):
        response = client.get(
            "/api/v1/users/stats",
            headers={"Authorization": f"Bearer {admin_auth_token}"},
        )
        assert response.status_code == 403

    def test_stats_success(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        superadmin_user: User,
        test_user: User,
    ):
        _ = superadmin_user, test_user
        response = client.get(
            "/api/v1/users/stats",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_accounts"] >= 2
        assert data["superadmin_count"] >= 1
        assert data["client_admin_count"] >= 1

    def test_list_users_success(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        superadmin_user: User,
        test_user: User,
    ):
        _ = superadmin_user, test_user
        response = client.get(
            "/api/v1/users/?skip=0&limit=100",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 2
        assert len(data["items"]) >= 2
        assert "hashed_password" not in data["items"][0]

    def test_list_users_forbidden_for_client_admin(self, client: TestClient, admin_auth_token: str):
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {admin_auth_token}"},
        )
        assert response.status_code == 403

    def test_update_user_email(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        test_user: User,
    ):
        new_email = f"updated-{uuid.uuid4().hex[:8]}@example.com"
        response = client.patch(
            f"/api/v1/users/{test_user.id}",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
            json={"email": new_email},
        )
        assert response.status_code == 200
        assert response.json()["email"] == new_email

    def test_update_user_empty_body(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        test_user: User,
    ):
        response = client.patch(
            f"/api/v1/users/{test_user.id}",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
            json={},
        )
        assert response.status_code == 400

    def test_delete_client_admin(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        db_session,
    ):
        user = User(
            email=f"delete-me-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=True,
            is_superadmin=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = client.delete(
            f"/api/v1/users/{user.id}",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
        )
        assert response.status_code == 204

    def test_delete_self_forbidden(
        self,
        client: TestClient,
        superadmin_auth_token: str,
        superadmin_user: User,
    ):
        response = client.delete(
            f"/api/v1/users/{superadmin_user.id}",
            headers={"Authorization": f"Bearer {superadmin_auth_token}"},
        )
        assert response.status_code == 403

    def test_delete_last_superadmin_forbidden(
        self,
        client: TestClient,
        db_session,
    ):
        """Cannot delete the only remaining superadmin account."""
        lone_super = User(
            email=f"lone-super-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False,
            is_superadmin=True,
        )
        actor = User(
            email=f"actor-super-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False,
            is_superadmin=True,
        )
        db_session.add(lone_super)
        db_session.add(actor)
        db_session.commit()
        db_session.refresh(actor)

        actor_token = create_access_token(actor.id)

        response = client.delete(
            f"/api/v1/users/{lone_super.id}",
            headers={"Authorization": f"Bearer {actor_token}"},
        )
        assert response.status_code == 204

        response2 = client.delete(
            f"/api/v1/users/{actor.id}",
            headers={"Authorization": f"Bearer {actor_token}"},
        )
        assert response2.status_code == 403
