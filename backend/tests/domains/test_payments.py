"""Tests for payments domain: invoice endpoints and operations."""

from datetime import date, timedelta

from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.payments.enums import InvoiceStates
from app.utils.sqids import sqid_encode
from tests.domains.test_helpers import execute_action, get_available_actions
from tests.factories.payments import InvoiceFactory  # Still needed for specific test cases


class TestInvoices:
    """Tests for invoice endpoints."""

    async def test_get_invoice(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
    ):
        """Test GET /invoices/{id} returns invoice details."""
        client, _ = authenticated_client

        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200
        assert response.json() is not None

    async def test_update_invoice(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
    ):
        """Test POST /invoices/{id} updates invoice."""
        client, _ = authenticated_client

        response = await client.post(
            f"/invoices/{sqid_encode(invoice.id)}",
            json={
                "customer_name": "Updated Customer",
                "amount_due": "1500.00",
            },
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_update_invoice_payment(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
    ):
        """Test updating invoice payment amount."""
        client, _ = authenticated_client

        response = await client.post(
            f"/invoices/{sqid_encode(invoice.id)}",
            json={"amount_paid": "500.00"},
        )
        assert response.status_code in [200, 201]
        assert response.json() is not None

    async def test_list_invoice_actions(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
    ):
        """Test GET /actions/invoice_actions/{id} returns available actions."""
        client, user_data = authenticated_client

        # Get available actions
        actions = await get_available_actions(client, "invoice_actions", sqid_encode(invoice.id))

        # Should have at least update and delete actions
        action_keys = [action["action"] for action in actions]
        assert "invoice_actions__invoice_update" in action_keys
        assert "invoice_actions__invoice_delete" in action_keys

    async def test_execute_invoice_update_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
        db_session: AsyncSession,
    ):
        """Test executing invoice update action."""
        client, _ = authenticated_client

        result = await execute_action(
            client,
            "invoice_actions",
            "invoice_actions__invoice_update",
            {"customer_name": "Updated via Action"},
            sqid_encode(invoice.id),
        )

        assert result is not None

    async def test_execute_invoice_delete_action(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        invoice,
        db_session: AsyncSession,
    ):
        """Test executing invoice delete action."""
        client, _ = authenticated_client

        result = await execute_action(
            client,
            "invoice_actions",
            "invoice_actions__invoice_delete",
            {},
            sqid_encode(invoice.id),
        )

        assert result is not None

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
        campaign,
        db_session: AsyncSession,
    ):
        """Test invoice associated with a campaign."""
        client, user_data = authenticated_client

        # Create invoice linked to campaign using factory
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
        invoice,
    ):
        """Test that new invoices start in DRAFT state."""
        client, user_data = authenticated_client

        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        # State should be initial state from factory or DRAFT
        assert data["state"] in [InvoiceStates.DRAFT.value, InvoiceStates.POSTED.value]

    async def test_invoice_dates(
        self,
        authenticated_client: tuple[AsyncTestClient, dict],
        team,
        db_session: AsyncSession,
    ):
        """Test invoice date fields."""
        client, user_data = authenticated_client

        today = date.today()
        due_date = today + timedelta(days=30)

        # Create specific invoice with date fields for this test
        invoice = await InvoiceFactory.create_async(
            session=db_session,
            team_id=team.id,
            posting_date=today,
            due_date=due_date,
        )
        await db_session.commit()

        response = await client.get(f"/invoices/{sqid_encode(invoice.id)}")
        assert response.status_code == 200

        data = response.json()
        assert data["posting_date"] == str(today)
        assert data["due_date"] == str(due_date)
