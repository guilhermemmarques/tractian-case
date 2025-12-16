import os
import json
import logging
from decouple import AutoConfig

from src.models.customer_models import CustomerWorkorderModel
from src.repositories.workorder_repository import WorkOrderRepository
from src.service.workorder_service import WorkOrderService

config = AutoConfig(search_path=".")

log = logging.getLogger(__name__)


class InboundProcessor:
    def __init__(self, repository: WorkOrderRepository):
        self.repository = repository
        self.data_inbound_dir: str = ""

        self._validate_and_set_env_vars()

    def _validate_and_set_env_vars(self):
        """Validate that all required environment variables are set."""

        data_inbound_dir = config("DATA_INBOUND_DIR", default=None)
        if not data_inbound_dir or not isinstance(data_inbound_dir, str):
            raise EnvironmentError(
                "Missing required environment variable: DATA_INBOUND_DIR"
            )

        self.data_inbound_dir = data_inbound_dir

    def read_json_file(self, file_path: str):
        """Read and load a JSON file."""

        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON from file {file_path}: {e}")
            return None
        except PermissionError as e:
            log.error(f"Permission error reading file {file_path}: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error reading file {file_path}: {e}")
            return None

    async def process_files(self):
        """Process inbound workorder from costumer to TracOS format."""

        log.info("Starting inbound workorder processing...")

        if not os.path.exists(self.data_inbound_dir):
            log.warning(f"Inbound directory {self.data_inbound_dir} does not exist.")
            return

        for filename in os.listdir(self.data_inbound_dir):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(self.data_inbound_dir, filename)
            log.info(f"Processing file: {filepath}")

            data = self.read_json_file(filepath)
            if data is None:
                log.error(f"Skipping file {filepath} due to read error.")
                continue

            try:
                client_workorder = CustomerWorkorderModel(**data)

                tracos_workorder = WorkOrderService.convert_customer_to_tracos_model(
                    client_workorder
                )

                await WorkOrderService.upsert_workorder(
                    self.repository, tracos_workorder, field="number"
                )

                log.info(
                    f"Successfully processed and inserted workorder {tracos_workorder.number} from file {filename}."
                )

            except Exception as e:
                log.error(f"Error processing file {filepath}: {e}")
                continue

        log.info("Inbound workorder processing completed.")
