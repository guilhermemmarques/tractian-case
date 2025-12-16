import pytest
import os
import json
from datetime import datetime

from src.modules.outbound import OutboundProcessor
from src.models.tracOS_models import TracOSWorkorderModel, TracOSWorkOrderStatusEnum


@pytest.fixture
async def outbound_data(workorder_repository):
    tracos_workorders = [
        TracOSWorkorderModel(
            number=1,
            status=TracOSWorkOrderStatusEnum.PENDING,
            title="Workorder 1",
            description="Description 1",
            createdAt=datetime(2025, 12, 14, 10, 0, 0),
            updatedAt=datetime(2025, 12, 14, 12, 0, 0),
            deleted=False,
            deletedAt=None,
        ),
        TracOSWorkorderModel(
            number=2,
            status=TracOSWorkOrderStatusEnum.COMPLETED,
            title="Workorder 2",
            description="Description 2",
            createdAt=datetime(2025, 12, 13, 9, 0, 0),
            updatedAt=datetime(2025, 12, 14, 11, 0, 0),
            deleted=False,
            deletedAt=None,
        ),
    ]

    for workorder in tracos_workorders:
        await workorder_repository.insert(workorder)

    return tracos_workorders


@pytest.mark.asyncio
async def test_outbound_pipeline(tmp_path, workorder_repository, outbound_data):
    # assert to make sure outbound_data has isSynced and syncedAt fields
    for workorder in outbound_data:
        assert workorder.isSynced is False
        assert workorder.syncedAt is None

    outbound_dir = tmp_path / "outbound"
    os.makedirs(outbound_dir, exist_ok=True)
    os.environ["DATA_OUTBOUND_DIR"] = str(outbound_dir)

    outbound_processor = OutboundProcessor(repository=workorder_repository)

    await outbound_processor.process_files()

    output_files = list(outbound_dir.iterdir())

    # Verifica o conteúdo dos arquivos
    for file in output_files:
        with open(file, "r") as f:
            data = json.load(f)
            if "workorder_1.json" in file.name:
                assert data["orderNo"] == 1
                assert data["isPending"] is True
                assert data["isDone"] is False
            elif "workorder_2.json" in file.name:
                assert data["orderNo"] == 2
                assert data["isPending"] is False
                assert data["isDone"] is True

    for workorder in outbound_data:
        stored_workorder = await workorder_repository.find_by_field(
            "number", workorder.number
        )
        assert stored_workorder.isSynced is True
        assert stored_workorder.syncedAt is not None
