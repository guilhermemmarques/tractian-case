from datetime import datetime
import pytest
import os
import json
from modules.inbound import InboundProcessor
from src.models.tracOS_models import TracOSWorkOrderStatusEnum


@pytest.fixture
def customer_data():
    now = datetime.now().replace(
        microsecond=(datetime.now().microsecond // 1000) * 1000
    )
    return {
        "orderNo": 1,
        "isActive": True,
        "isCanceled": False,
        "isDeleted": False,
        "isDone": False,
        "isOnHold": False,
        "isPending": True,
        "isSynced": False,
        "summary": "Test workorder summary",
        "creationDate": now.isoformat(),
        "lastUpdateDate": now.isoformat(),
        "deletedDate": None,
    }


@pytest.mark.asyncio
async def test_inbound_pipeline(tmp_path, workorder_repository, customer_data):
    """Test end-to-end inbound processing of workorder files."""

    inbound_dir = tmp_path / "inbound"
    os.makedirs(inbound_dir, exist_ok=True)
    os.environ["DATA_INBOUND_DIR"] = str(inbound_dir)

    test_file_path = inbound_dir / "workorder_001.json"
    with open(test_file_path, "w") as f:
        json.dump(customer_data, f)

    inbound_processor = InboundProcessor(repository=workorder_repository)

    await inbound_processor.process_files()

    stored_workorder = await workorder_repository.find_by_field(
        "number", customer_data["orderNo"]
    )

    assert stored_workorder is not None
    assert stored_workorder.number == customer_data["orderNo"]
    assert stored_workorder.title == customer_data["summary"]
    assert stored_workorder.description == customer_data["summary"]
    assert stored_workorder.createdAt.isoformat() == customer_data["creationDate"]
    assert stored_workorder.updatedAt.isoformat() == customer_data["lastUpdateDate"]
    assert stored_workorder.deleted == customer_data["isDeleted"]
    assert stored_workorder.status == TracOSWorkOrderStatusEnum.PENDING
