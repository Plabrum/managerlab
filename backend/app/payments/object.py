from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.objects.base import BaseObject
from app.objects.enums import ObjectTypes
from app.objects.schemas import (
    ObjectDetailDTO,
    ObjectListDTO,
    ObjectListRequest,
    ObjectFieldDTO,
    FieldType,
)
from app.payments.models import Invoice
from app.utils.sqids import sqid_encode


class InvoiceObject(BaseObject):
    object_type = ObjectTypes.Invoice

    @classmethod
    def to_detail_dto(cls, invoice: Invoice) -> ObjectDetailDTO:
        fields = [
            ObjectFieldDTO(
                key="invoice_number",
                value=invoice.invoice_number,
                type=FieldType.Int,
                label="Invoice Number",
                editable=False,
            ),
            ObjectFieldDTO(
                key="customer_name",
                value=invoice.customer_name,
                type=FieldType.String,
                label="Customer Name",
                editable=True,
            ),
            ObjectFieldDTO(
                key="customer_email",
                value=invoice.customer_email,
                type=FieldType.Email,
                label="Customer Email",
                editable=True,
            ),
            ObjectFieldDTO(
                key="posting_date",
                value=invoice.posting_date.isoformat()
                if invoice.posting_date
                else None,
                type=FieldType.Date,
                label="Posting Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="due_date",
                value=invoice.due_date.isoformat() if invoice.due_date else None,
                type=FieldType.Date,
                label="Due Date",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_due",
                value=float(invoice.amount_due),
                type=FieldType.USD,
                label="Amount Due",
                editable=True,
            ),
            ObjectFieldDTO(
                key="amount_paid",
                value=float(invoice.amount_paid),
                type=FieldType.USD,
                label="Amount Paid",
                editable=True,
            ),
            ObjectFieldDTO(
                key="description",
                value=invoice.description,
                type=FieldType.Text,
                label="Description",
                editable=True,
            ),
            ObjectFieldDTO(
                key="notes",
                value=invoice.notes,
                type=FieldType.Text,
                label="Notes",
                editable=True,
            ),
        ]

        return ObjectDetailDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoice,
            state=invoice.state.name,
            fields=fields,
            actions=[],
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
            children=[],
            parents=[],
        )

    @classmethod
    def to_list_dto(cls, invoice: Invoice) -> ObjectListDTO:
        return ObjectListDTO(
            id=sqid_encode(invoice.id),
            object_type=ObjectTypes.Invoice,
            title=f"Invoice #{invoice.invoice_number}",
            subtitle=f"{invoice.customer_name} - ${invoice.amount_due}",
            state=invoice.state.name,
            actions=[],
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
        )

    @classmethod
    async def query_from_request(
        cls, session: AsyncSession, request: ObjectListRequest
    ):
        query = select(Invoice)

        # Apply filters if provided
        if request.filters:
            if "customer_name" in request.filters:
                query = query.where(
                    Invoice.customer_name.ilike(f"%{request.filters['customer_name']}%")
                )
            if "customer_email" in request.filters:
                query = query.where(
                    Invoice.customer_email.ilike(
                        f"%{request.filters['customer_email']}%"
                    )
                )
            if "invoice_number" in request.filters:
                query = query.where(
                    Invoice.invoice_number == request.filters["invoice_number"]
                )
            if "search" in request.filters:
                search_term = f"%{request.filters['search']}%"
                query = query.where(
                    (Invoice.customer_name.ilike(search_term))
                    | (Invoice.customer_email.ilike(search_term))
                    | (Invoice.description.ilike(search_term))
                )

        # Apply sorting
        if request.sort_by:
            sort_column = getattr(Invoice, request.sort_by, None)
            if sort_column:
                if request.sort_order == "asc":
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
        else:
            # Default sort by due_date desc
            query = query.order_by(Invoice.due_date.desc())

        return query

    @classmethod
    async def get_by_id(cls, session: AsyncSession, object_id: int) -> Invoice:
        result = await session.get(Invoice, object_id)
        if not result:
            raise ValueError(f"Invoice with id {object_id} not found")
        return result

    @classmethod
    async def get_list(
        cls, session: AsyncSession, request: ObjectListRequest
    ) -> tuple[Sequence[Invoice], int]:
        query = await cls.query_from_request(session, request)
        total_rows = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_rows.scalar_one()

        # Apply pagination
        query = query.offset(request.offset).limit(request.limit)

        # Execute query
        result = await session.execute(query)
        invoices = result.scalars().all()

        return invoices, total
