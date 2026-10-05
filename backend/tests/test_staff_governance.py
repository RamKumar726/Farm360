import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.jwt import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.branches import Branch
from app.models.users import User, UserRole
from app.models.zones import Zone


class StaffGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)

        def override_db():
            with cls.Session() as db:
                yield db

        app.dependency_overrides[get_db] = override_db
        cls.client = TestClient(app)
        with cls.Session() as db:
            db.add_all([
                Branch(id="branch-a", name="Branch A"),
                Branch(id="branch-b", name="Branch B"),
            ])
            db.flush()
            db.add_all([
                Zone(id="zone-a", name="Zone A", branch_id="branch-a"),
                Zone(id="zone-b", name="Zone B", branch_id="branch-b"),
            ])
            db.flush()
            password = hash_password("Safe-Test-Password-1")
            db.add_all([
                User(id="founder", name="Founder", email="founder@example.com", password_hash=password, role=UserRole.founder),
                User(id="admin-a", name="Admin A", email="admin-a@example.com", password_hash=password, role=UserRole.zone_admin, branch_id="branch-a", zone_id="zone-a"),
                User(id="employee-a", name="Employee A", email="employee-a@example.com", password_hash=password, role=UserRole.employee, branch_id="branch-a", zone_id="zone-a"),
                User(id="employee-b", name="Employee B", email="employee-b@example.com", password_hash=password, role=UserRole.employee, branch_id="branch-b", zone_id="zone-b"),
            ])
            db.commit()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.engine.dispose()

    @staticmethod
    def auth(user_id):
        return {"Authorization": f"Bearer {create_access_token({'sub': user_id})}"}

    def test_founder_can_crud_agriculture_officer(self):
        response = self.client.post("/users", headers=self.auth("founder"), json={
            "name": "Agriculture Officer", "email": "ao@example.com",
            "password": "Secure-Staff-Password-1", "role": "agri_officer",
            "branch_id": "branch-a", "zone_id": "zone-a",
        })
        self.assertEqual(response.status_code, 200, response.text)
        user_id = response.json()["data"]["id"]

        response = self.client.get(f"/users/{user_id}", headers=self.auth("founder"))
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.patch(f"/users/{user_id}", headers=self.auth("founder"), json={"name": "Senior Agriculture Officer"})
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.delete(f"/users/{user_id}", headers=self.auth("founder"))
        self.assertEqual(response.status_code, 200, response.text)

    def test_zone_admin_cannot_grant_zone_admin_role(self):
        response = self.client.post("/users", headers=self.auth("admin-a"), json={
            "name": "Unauthorized Admin", "email": "blocked@example.com",
            "password": "Secure-Staff-Password-1", "role": "zone_admin",
            "branch_id": "branch-a", "zone_id": "zone-a",
        })
        self.assertEqual(response.status_code, 403, response.text)

    def test_zone_admin_cannot_modify_other_branch(self):
        response = self.client.patch(
            "/users/employee-b", headers=self.auth("admin-a"), json={"name": "Cross Branch Edit"},
        )
        self.assertEqual(response.status_code, 403, response.text)

    def test_employee_cannot_promote_self(self):
        response = self.client.patch(
            "/users/employee-a", headers=self.auth("employee-a"), json={"role": "founder"},
        )
        self.assertEqual(response.status_code, 403, response.text)


if __name__ == "__main__":
    unittest.main()
