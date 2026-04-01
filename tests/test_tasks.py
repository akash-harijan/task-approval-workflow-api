import pytest
from fastapi.testclient import TestClient
from main import app
from repositories.task_repo import task_repository

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repo():
    task_repository._store.clear()
    yield
    task_repository._store.clear()


def test_create_data_access_task():
    payload = {
        "type": "data_access",
        "title": "Access customer dataset",
        "requested_by": "alice",
        "dataset_name": "customers_eu",
        "access_level": "read",
        "data_classification": "confidential",
    }
    r = client.post("/tasks/", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "PENDING"
    assert body["dataset_name"] == "customers_eu"
    assert "id" in body



def test_approve_task():
    payload = {
        "type": "resource_provision",
        "title": "Provision dev VM",
        "requested_by": "carol",
        "resource_type": "vm",
        "environment": "dev",
        "estimated_cost_eur": 120.0,
    }
    created = client.post("/tasks/", json=payload).json()
    task_id = created["id"]

    r = client.patch(f"/tasks/{task_id}/approve", json={"approved_by": "manager"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "APPROVED"
    assert body["resolved_at"] is not None


def test_reject_task():
    payload = {
        "type": "data_access",
        "title": "Access restricted logs",
        "requested_by": "dave",
        "dataset_name": "security_logs",
        "access_level": "read",
        "data_classification": "restricted",
    }
    task_id = client.post("/tasks/", json=payload).json()["id"]

    r = client.patch(
        f"/tasks/{task_id}/reject",
        json={
            "rejected_by": "security_team",
            "reason": "Insufficient justification provided for access.",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "REJECTED"
    assert "Insufficient justification" in body["rejection_reason"]


def test_cannot_approve_already_rejected_task():
    payload = {
        "type": "data_access",
        "title": "Attempt double action",
        "requested_by": "eve",
        "dataset_name": "hr_data",
        "access_level": "read",
        "data_classification": "internal",
    }
    task_id = client.post("/tasks/", json=payload).json()["id"]
    client.patch(
        f"/tasks/{task_id}/reject",
        json={"rejected_by": "mgr", "reason": "Not needed right now."},
    )

    r = client.patch(f"/tasks/{task_id}/approve", json={"approved_by": "mgr"})
    assert r.status_code == 409


def test_config_change_downtime_without_rollback_plan_fails():
    payload = {
        "type": "config_change",
        "title": "Risky change with no rollback",
        "requested_by": "frank",
        "service_name": "payments",
        "change_description": "Switch database driver from psycopg2 to asyncpg in production",
        "requires_downtime": True,
    }
    r = client.post("/tasks/", json=payload)
    assert r.status_code == 422
