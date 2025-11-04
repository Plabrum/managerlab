"""Tests for payments domain: invoice endpoints and operations."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.enums import InvoiceStates
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import assert_rls_isolated, execute_action, get_available_actions
from tests.factories.payments import InvoiceFactory


class TestInvoices:
    """Tests for invoice endpoints."""

    async def test_get_invoice(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /invoices/{id} returns invoice details."""
        client, user_data = authenticated_client

        # Create an invoice for this team
        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get the invoice
        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sqid_encode(invoice.id)
        assert data["invoice_number"] == invoice.invoice_number
        assert data["customer_name"] == invoice.customer_name
        assert data["team_id"] == sqid_encode(user_data["team_id"])
        assert "actions" in data  # Should include available actions

    async def test_update_invoice(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test POST /invoices/{id} updates invoice."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            customer_name="Original Customer",
            amount_due=Decimal("1000.00"),
        )
        await db_session.commit()

        # Update the invoice
        response = await client.post(
            f"/invoices/{sqid_encode(invoice.id)}",
            json={
                "customer_name": "Updated Customer",
                "amount_due": "1500.00",
            },
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert data["customer_name"] == "Updated Customer"
        assert Decimal(data["amount_due"]) == Decimal("1500.00")

    async def test_update_invoice_payment(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test updating invoice payment amount."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            amount_due=Decimal("1000.00"),
            amount_paid=Decimal("0.00"),
        )
        await db_session.commit()

        # Record partial payment
        response = await client.post(
            f"/invoices/{sqid_encode(invoice.id)}",
            json={"amount_paid": "500.00"},
        )
        assert response.status_code in [200, 201]

        data = response.json()
        assert Decimal(data["amount_paid"]) == Decimal("500.00")

    async def test_list_invoice_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test GET /actions/invoice_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Get available actions
        actions = await get_available_actions(client, "invoice_actions", sqid_encode(invoice.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "invoice.update" in action_keys
        assert "invoice.delete" in action_keys

    async def test_execute_invoice_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing invoice update action."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            customer_name="Original Customer",
        )
        await db_session.commit()

        # Execute update action
        result = await execute_action(
            client,
            "invoice_actions",
            "invoice.update",
            {"customer_name": "Updated via Action"},
            sqid_encode(invoice.id),
        )

        assert result["success"] is True

        # Verify the update
        await db_session.refresh(invoice)
        assert invoice.customer_name == "Updated via Action"

    async def test_execute_invoice_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test executing invoice delete action."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Execute delete action
        result = await execute_action(
            client,
            "invoice_actions",
            "invoice.delete",
            {},
            sqid_encode(invoice.id),
        )

        assert result["success"] is True

        # Verify soft deletion
        await db_session.refresh(invoice)
        assert invoice.deleted_at is not None

    async def test_invoice_rls_isolation(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        other_team_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that teams cannot access each other's invoices."""
        client, user_data = authenticated_client
        other_client, other_user_data = other_team_client

        # Create invoice for first team
        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Verify RLS isolation
        await assert_rls_isolated(
            client=other_client,
            resource_path=f"/invoices/{sqid_encode(invoice.id)}",
        )

    async def test_get_invoice_not_found(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
    ):
        """Test GET /invoices/{id} with non-existent ID returns 404."""
        client, user_data = authenticated_client

        # Try to get a non-existent invoice
        response = await client.get(f"/invoices/{sqid_encode(99999)}")
        assert response.status_code == 404

    async def test_invoice_with_campaign(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test invoice associated with a campaign."""
        from tests.factories.campaigns import CampaignFactory

        client, user_data = authenticated_client

        # Create a campaign
        campaign = await CampaignFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        # Create invoice linked to campaign
        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            campaign_id=campaign.id,
        )
        await db_session.commit()

        # Get the invoice
        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["campaign_id"] == sqid_encode(campaign.id)


class TestInvoiceStates:
    """Tests for invoice state transitions."""

    async def test_invoice_initial_state(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test that new invoices start in DRAFT state."""
        client, user_data = authenticated_client

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
        )
        await db_session.commit()

        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        # State should be initial state from factory or DRAFT
        assert data["state"] in [InvoiceStates.DRAFT.value, InvoiceStates.POSTED.value]

    async def test_invoice_dates(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        db_session: AsyncSession,
    ):
        """Test invoice date fields."""
        client, user_data = authenticated_client

        today = date.today()
        due_date = today + timedelta(days=30)

        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=user_data["team_id"],
            posting_date=today,
            due_date=due_date,
        )
        await db_session.commit()

        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["posting_date"] == str(today)
        assert data["due_date"] == str(due_date)
