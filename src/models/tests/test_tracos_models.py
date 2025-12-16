import pytest
from datetime import datetime
from src.models.tracOS_models import TracOSWorkorderModel, TracOSWorkOrderStatusEnum


@pytest.fixture
def workorder_data():
    return {
        "number": 12345,
        "status": TracOSWorkOrderStatusEnum.PENDING,
        "title": "Test Workorder",
        "description": "This is a test workorder.",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "deleted": False,
        "deletedAt": None,
    }


def test_tracos_workorder_model_creation(workorder_data):
    workorder = TracOSWorkorderModel(**workorder_data)

    assert workorder.number == workorder_data["number"]
    assert workorder.status == workorder_data["status"]
    assert workorder.title == workorder_data["title"]
    assert workorder.description == workorder_data["description"]
    assert workorder.createdAt == workorder_data["createdAt"]
    assert workorder.updatedAt == workorder_data["updatedAt"]
    assert workorder.deleted == workorder_data["deleted"]
    assert workorder.deletedAt == workorder_data["deletedAt"]


def test_tracos_workorder_model_defaults():
    workorder = TracOSWorkorderModel(
        number=67890,
        title="Default Workorder",
        description="This workorder uses default values.",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )

    assert workorder.status == TracOSWorkOrderStatusEnum.PENDING
    assert workorder.deleted is False
    assert workorder.deletedAt is None


def test_tracos_workorder_model_invalid_data():
    with pytest.raises(ValueError):
        TracOSWorkorderModel(
            number="not_an_integer",
            title=123,
            description=456,
            createdAt="not_a_datetime",
            updatedAt="not_a_datetime",
        )
