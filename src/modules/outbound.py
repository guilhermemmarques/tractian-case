import os
import json
import logging
from decouple import AutoConfig
from datetime import datetime

from src.repositories.workorder_repository import WorkOrderRepository
from src.service.workorder_service import WorkOrderService

log = logging.getLogger(__name__)
config = AutoConfig(search_path=".")


class OutboundProcessor:
    def __init__(self, repository: WorkOrderRepository):
        self.repository = repository
        self.data_outbound_dir: str = ""

        self._validate_and_set_env_vars()

    def _validate_and_set_env_vars(self):
        """Validate that all required environment variables are set."""

        data_outbound_dir = config("DATA_OUTBOUND_DIR", default=None)
        if not data_outbound_dir or not isinstance(data_outbound_dir, str):
            raise EnvironmentError(
                "Missing required environment variable: DATA_OUTBOUND_DIR"
            )
        self.data_outbound_dir = data_outbound_dir

    def write_json_file(self, file_path: str, data: dict):
        """Write data to a JSON file."""

        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4, default=json_serializer)
        except PermissionError as e:
            log.error(f"Permission error writing file {file_path}: {e}")
        except Exception as e:
            log.error(f"Unexpected error writing file {file_path}: {e}")

    async def process_files(self):
        """Process outbound workorder from TracOS to customer format."""

        log.info("Starting outbound workorder processing...")

        # Ensure outbound directory exists
        os.makedirs(self.data_outbound_dir, exist_ok=True)

        # Fetch workorders from the repository where isSynced is False
        workorders = await self.repository.find_is_synced_workorders(is_synced=False)

        for workorder in workorders:
            try:
                log.info(f"Processing workorder: {workorder.number}")

                customer_workorder = WorkOrderService.convert_tracOS_to_customer_model(
                    workorder
                )

                output_filepath = os.path.join(
                    self.data_outbound_dir,
                    f"workorder_{customer_workorder.orderNo}.json",
                )
                self.write_json_file(output_filepath, customer_workorder.model_dump())

                log.info(
                    f"Successfully processed and wrote workorder {customer_workorder.orderNo} to file."
                )

                # Mark workorder as synced
                workorder.isSynced = True
                workorder.syncedAt = datetime.now()
                await WorkOrderService.upsert_workorder(
                    self.repository, workorder, field="number"
                )
            except Exception as e:
                log.error(f"Error processing workorder {workorder.number}: {e}")
