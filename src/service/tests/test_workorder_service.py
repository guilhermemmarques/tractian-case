import pytest
from datetime import datetime
from src.service.workorder_service import WorkOrderService
from src.models.customer_models import CustomerWorkorderModel
from src.models.tracOS_models import TracOSWorkOrderStatusEnum, TracOSWorkorderModel


@pytest.fixture
def customer_workorder():
    return CustomerWorkorderModel(
        orderNo=2002,
        isActive=True,
        isCanceled=False,
        isDeleted=False,
        isDone=False,
        isOnHold=False,
        isPending=True,
        isSynced=False,
        summary="Test Workorder from Customer",
        creationDate=datetime.now(),
        lastUpdateDate=datetime.now(),
        deletedDate=None,
    )


@pytest.fixture
def tracOS_workorder():
    return TracOSWorkorderModel(
        number=2002,
        status=TracOSWorkOrderStatusEnum.COMPLETED,
        title="Test Workorder from TracOS",
        description="Description",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        deleted=False,
        deletedAt=None,
    )


def test_convert_customer_to_tracos_model(customer_workorder):
    tracos_workorder = WorkOrderService.convert_customer_to_tracos_model(
        customer_workorder
    )

    assert isinstance(tracos_workorder, TracOSWorkorderModel)
    assert tracos_workorder.number == customer_workorder.orderNo
    assert tracos_workorder.status == TracOSWorkOrderStatusEnum.PENDING
    assert tracos_workorder.title == customer_workorder.summary
    assert tracos_workorder.description == customer_workorder.summary
    assert tracos_workorder.isSynced is False
    assert tracos_workorder.createdAt == customer_workorder.creationDate
    assert tracos_workorder.updatedAt == customer_workorder.lastUpdateDate
    assert tracos_workorder.deleted == customer_workorder.isDeleted
    assert tracos_workorder.deletedAt == customer_workorder.deletedDate


@pytest.mark.asyncio
async def test_upsert_workorder_insert(workorder_repository):
    tracos_workorder = TracOSWorkorderModel(
        number=3003,
        status=TracOSWorkOrderStatusEnum.PENDING,
        title="New Workorder",
        description="Description",
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        deleted=False,
        deletedAt=None,
    )

    await WorkOrderService.upsert_workorder(
        workorder_repository, tracos_workorder, "number"
    )

    inserted_workorder = await workorder_repository.find_by_field("number", 3003)
    assert inserted_workorder is not None
    assert inserted_workorder.number == 3003
    assert inserted_workorder.title == "New Workorder"


def test_convert_tracOS_to_customer_model(tracOS_workorder):
    customer_workorder = WorkOrderService.convert_tracOS_to_customer_model(
        tracOS_workorder
    )

    assert isinstance(customer_workorder, CustomerWorkorderModel)
    assert customer_workorder.orderNo == tracOS_workorder.number
    assert customer_workorder.isDone is True
    assert customer_workorder.isPending is False
    assert customer_workorder.summary == tracOS_workorder.title
    assert customer_workorder.creationDate == tracOS_workorder.createdAt
    assert customer_workorder.lastUpdateDate == tracOS_workorder.updatedAt
    assert customer_workorder.isDeleted == tracOS_workorder.deleted
    assert customer_workorder.deletedDate == tracOS_workorder.deletedAt


@pytest.mark.asyncio
async def test_update_workorder(workorder_repository, tracOS_workorder):
    await workorder_repository.insert(tracOS_workorder)

    tracOS_workorder.title = "Updated Workorder Title"
    await WorkOrderService.upsert_workorder(
        workorder_repository, tracOS_workorder, "number"
    )

    updated_workorder = await workorder_repository.find_by_field(
        "number", tracOS_workorder.number
    )
    assert updated_workorder is not None
    assert updated_workorder.title == "Updated Workorder Title"
