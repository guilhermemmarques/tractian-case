"""Entrypoint for the application."""

import asyncio
import logging

from modules.inbound import InboundProcessor
from modules.outbound import OutboundProcessor
from src.repositories.repository_factory import RepositoryFactory


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

log = logging.getLogger(__name__)


async def inbount_process():
    log.info("Processing inbound files...")
    try:
        repository = await RepositoryFactory.get_workorder_repository()
        inbound_processor = InboundProcessor(repository)
        await inbound_processor.process_files()
        log.info("Inbound files processed.")
    except Exception as e:
        log.error(
            f"Aborting inbound processing due to repository connection failure. Error: {e}"
        )


async def outbound_process():
    log.info("Processing outbound files...")
    try:
        repository = await RepositoryFactory.get_workorder_repository()
        outbound_processor = OutboundProcessor(repository)
        await outbound_processor.process_files()
        log.info("Outbound files processed.")
    except Exception as e:
        log.error(
            f"Aborting Outbound processing due to repository connection failure. Error: {e}"
        )


async def main():
    log.info("Starting integration pipeline...")

    # Process inbound files (Client -> TracOS)
    await inbount_process()

    # process outbound files (TracOS -> Client)
    await outbound_process()

    log.info("Integration pipeline complete.")


if __name__ == "__main__":
    asyncio.run(main())
