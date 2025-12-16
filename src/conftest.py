import pytest
import docker
import time
from motor.motor_asyncio import AsyncIOMotorClient
from src.repositories.repository_factory import RepositoryFactory


@pytest.fixture(scope="session")
def docker_compose():
    """Raise a MongoDB container for testing."""
    client = docker.from_env()
    container_name = "tractian-mongo-test"

    try:
        try:
            container = client.containers.get(container_name)
            if container.status == "running":
                # reuse the existing container
                yield
                return
            else:
                # Remove the container if it is stopped
                container.remove()
        except docker.errors.NotFound:
            pass

        # Start the container with the name 'tractian-mongo-test'
        client.containers.run(
            "mongo:5.0",
            name=container_name,
            ports={"27017/tcp": 27017},
            detach=True,
        )
        time.sleep(5)  # Wait for MongoDB to initialize
        yield
    finally:
        # Stop and remove the container after tests
        try:
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass


@pytest.fixture(scope="function")
async def mongo_client(docker_compose):
    """Create a MongoDB instance for each test."""
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)

    # Ensure the database is cleaned before each test
    db = client["tractian"]
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()

    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="function")
async def workorder_repository(mongo_client):
    """Create a repository instance using the in-memory MongoDB."""
    repository = await RepositoryFactory.get_workorder_repository()
    return repository
