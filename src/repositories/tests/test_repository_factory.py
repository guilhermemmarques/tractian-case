import pytest


@pytest.mark.asyncio
async def test_get_worker_repository(workorder_repository):
    """Test if the repository factory creates a valid repository instance."""
    assert workorder_repository is not None
