import logging

from src.models.customer_models import CustomerWorkorderModel
from src.models.tracOS_models import TracOSWorkorderModel, TracOSWorkOrderStatusEnum

log = logging.getLogger(__name__)


class WorkOrderService:
    @staticmethod
    def convert_customer_to_tracos_model(
        client_workorder: CustomerWorkorderModel,
    ) -> TracOSWorkorderModel:
        """Convert a costumer model from the client to the TracOS format."""

        status_mapping = {
            "isPending": TracOSWorkOrderStatusEnum.PENDING,
            "isOnHold": TracOSWorkOrderStatusEnum.ON_HOLD,
            "isDone": TracOSWorkOrderStatusEnum.COMPLETED,
            "isCanceled": TracOSWorkOrderStatusEnum.CANCELLED,
            "isDeleted": TracOSWorkOrderStatusEnum.DELETED,
        }

        for key, tracos_status in status_mapping.items():
            if getattr(client_workorder, key, False):
                status = tracos_status
                break

        return TracOSWorkorderModel(
            number=client_workorder.orderNo,
            status=status or TracOSWorkOrderStatusEnum.PENDING,
            title=client_workorder.summary,
            description=client_workorder.summary,
            createdAt=client_workorder.creationDate,
            updatedAt=client_workorder.lastUpdateDate,
            deleted=client_workorder.isDeleted,
            deletedAt=client_workorder.deletedDate,
        )

    @staticmethod
    async def upsert_workorder(
        repository, tracos_workorder: TracOSWorkorderModel, field: str
    ):
        """Upsert a workorder into the repository."""

        existing_workorder = await repository.find_by_field(
            field, getattr(tracos_workorder, field)
        )

        if existing_workorder:
            await repository.update(existing_workorder.number, tracos_workorder)
            log.info(
                f"Updated workorder {getattr(tracos_workorder, field)} in the database."
            )

        else:
            await repository.insert(tracos_workorder)
            log.info(
                f"Inserted workorder {getattr(tracos_workorder, field)} into the database."
            )

    @staticmethod
    def convert_tracOS_to_customer_model(
        tracos_workorder: TracOSWorkorderModel,
    ) -> CustomerWorkorderModel:
        """Convert a TracOS workorder model to the customer format."""

        status_flags = {
            "isPending": False,
            "isOnHold": False,
            "isDone": False,
            "isCanceled": False,
            "isDeleted": False,
        }

        status_mapping = {
            TracOSWorkOrderStatusEnum.PENDING: "isPending",
            TracOSWorkOrderStatusEnum.ON_HOLD: "isOnHold",
            TracOSWorkOrderStatusEnum.COMPLETED: "isDone",
            TracOSWorkOrderStatusEnum.CANCELLED: "isCanceled",
            TracOSWorkOrderStatusEnum.DELETED: "isDeleted",
        }

        flag_key = status_mapping.get(tracos_workorder.status)
        if flag_key:
            status_flags[flag_key] = True

        return CustomerWorkorderModel(
            orderNo=tracos_workorder.number,
            summary=tracos_workorder.title,
            creationDate=tracos_workorder.createdAt,
            lastUpdateDate=tracos_workorder.updatedAt,
            deletedDate=tracos_workorder.deletedAt,
            **status_flags,
        )
