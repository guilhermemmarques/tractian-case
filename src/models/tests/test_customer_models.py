import pytest
from datetime import datetime

from src.models.customer_models import CustomerWorkorderModel


@pytest.fixture
def customer_workorder_data():
    return {
        "orderNo": 1001,
        "isActive": True,
        "isCanceled": False,
        "isDeleted": False,
        "isDone": False,
        "isOnHold": False,
        "isPending": True,
        "isSynced": False,
        "summary": "Test Customer Workorder",
        "creationDate": datetime.now(),
        "lastUpdateDate": datetime.now(),
        "deletedDate": None,
    }


def test_customer_workorder_model_creation(customer_workorder_data):
    customer_workorder = CustomerWorkorderModel(**customer_workorder_data)

    assert customer_workorder.orderNo == customer_workorder_data["orderNo"]
    assert customer_workorder.isActive == customer_workorder_data["isActive"]
    assert customer_workorder.isCanceled == customer_workorder_data["isCanceled"]
    assert customer_workorder.isDeleted == customer_workorder_data["isDeleted"]
    assert customer_workorder.isDone == customer_workorder_data["isDone"]
    assert customer_workorder.isOnHold == customer_workorder_data["isOnHold"]
    assert customer_workorder.isPending == customer_workorder_data["isPending"]
    assert customer_workorder.isSynced == customer_workorder_data["isSynced"]
    assert customer_workorder.summary == customer_workorder_data["summary"]
    assert customer_workorder.creationDate == customer_workorder_data["creationDate"]
    assert (
        customer_workorder.lastUpdateDate == customer_workorder_data["lastUpdateDate"]
    )
    assert customer_workorder.deletedDate == customer_workorder_data["deletedDate"]


def test_customer_workorder_model_invalid_data():
    with pytest.raises(ValueError):
        CustomerWorkorderModel(
            orderNo="not_an_integer",
            isActive="not_a_boolean",
            isCanceled="not_a_boolean",
            isDeleted="not_a_boolean",
            isDone="not_a_boolean",
            isOnHold="not_a_boolean",
            isPending="not_a_boolean",
            isSynced="not_a_boolean",
            summary=123,
            creationDate="not_a_datetime",
            lastUpdateDate="not_a_datetime",
            deletedDate="not_a_datetime",
        )
