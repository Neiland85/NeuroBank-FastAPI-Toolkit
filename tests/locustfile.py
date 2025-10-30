"""Locust load testing configuration for NeuroBank FastAPI Toolkit."""

import random
from locust import HttpUser, task, between


class NeuroBankUser(HttpUser):
    """Simula un usuario típico de NeuroBank."""

    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        response = self.client.post(
            "/api/auth/login",
            data={"username": "test_user", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {"X-API-Key": "test_api_key"}

    @task(10)
    def health_check(self):
        self.client.get("/health")

    @task(5)
    def get_root(self):
        self.client.get("/")

    @task(3)
    def get_current_user(self):
        self.client.get("/api/auth/me", headers=self.headers)

    @task(2)
    def list_users(self):
        self.client.get("/api/users/", headers=self.headers)

    @task(2)
    def list_roles(self):
        self.client.get("/api/roles/", headers=self.headers)

    @task(1)
    def backoffice_dashboard(self):
        self.client.get("/backoffice/")

    @task(1)
    def backoffice_metrics(self):
        self.client.get("/backoffice/api/metrics")


class AdminUser(HttpUser):
    """Simula un usuario administrador con operaciones más pesadas."""

    wait_time = between(2, 5)
    host = "http://localhost:8000"

    def on_start(self):
        response = self.client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def list_all_users(self):
        self.client.get("/api/users/?skip=0&limit=100", headers=self.headers)

    @task(3)
    def create_user(self):
        user_id = random.randint(1000, 9999)
        self.client.post(
            "/api/users/",
            json={
                "username": f"user_{user_id}",
                "email": f"user_{user_id}@example.com",
                "password": "TestPass123!",
                "full_name": f"Test User {user_id}",
            },
            headers=self.headers,
        )

    @task(2)
    def manage_roles(self):
        self.client.get("/api/roles/", headers=self.headers)

    @task(1)
    def backoffice_admin_panel(self):
        self.client.get("/backoffice/admin/users", headers=self.headers)

