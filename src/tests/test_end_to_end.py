from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
import os
import json
from src.modules.inbound import InboundProcessor
from src.modules.outbound import OutboundProcessor
from src.models.tracOS_models import TracOSWorkOrderStatusEnum
from src.main import main


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
async def test_end_to_end_pipeline(tmp_path, workorder_repository, customer_data):
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

    outbound_dir = tmp_path / "outbound"
    os.makedirs(outbound_dir, exist_ok=True)
    os.environ["DATA_OUTBOUND_DIR"] = str(outbound_dir)

    outbound_processor = OutboundProcessor(repository=workorder_repository)
    await outbound_processor.process_files()

    output_files = list(outbound_dir.iterdir())
    assert len(output_files) == 1

    for file in output_files:
        with open(file, "r") as f:
            data = json.load(f)
            assert data["orderNo"] == customer_data["orderNo"]
            assert data["isPending"] is True
            assert data["isDone"] is False
            assert data["summary"] == customer_data["summary"]
            assert data["creationDate"] == customer_data["creationDate"]
            assert data["lastUpdateDate"] == customer_data["lastUpdateDate"]
            assert data["deletedDate"] == customer_data["deletedDate"]


@pytest.mark.asyncio
async def test_main_execution():
    with patch("src.main.InboundProcessor") as MockInboundProcessor, patch(
        "src.main.OutboundProcessor"
    ) as MockOutboundProcessor, patch(
        "src.main.RepositoryFactory.get_workorder_repository", new_callable=AsyncMock
    ) as mock_get_repository:
        mock_repository = AsyncMock()
        mock_get_repository.return_value = mock_repository

        mock_inbound_processor = AsyncMock()
        MockInboundProcessor.return_value = mock_inbound_processor

        mock_outbound_processor = AsyncMock()
        MockOutboundProcessor.return_value = mock_outbound_processor

        await main()

        MockInboundProcessor.assert_called_once_with(mock_repository)
        MockOutboundProcessor.assert_called_once_with(mock_repository)
        mock_inbound_processor.process_files.assert_awaited_once()
        mock_outbound_processor.process_files.assert_awaited_once()
