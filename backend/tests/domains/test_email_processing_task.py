"""Smoke tests for inbound email processing task."""

from email.message import EmailMessage
from unittest.mock import Mock

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.emails.enums import InboundEmailState
from app.emails.tasks import process_inbound_email_task
from tests.factories.emails import InboundEmailFactory


async def test_task_processes_email_with_metadata(
    db_session: AsyncSession,
):
    """Test task successfully processes an email and extracts metadata."""
    # Create sample email
    msg = EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "contracts@tryarive.com"
    msg["Subject"] = "Test Contract Submission"
    msg["Date"] = "Mon, 13 Nov 2023 10:30:00 -0500"
    msg["Message-ID"] = "<test123@mail.example.com>"
    msg.set_content("This is a test email body.")
    email_bytes = msg.as_bytes()

    # Create inbound email record
    email = await InboundEmailFactory.create_async(
        session=db_session,
        state=InboundEmailState.RECEIVED,
    )
    await db_session.commit()

    # Mock S3 client
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(return_value=email_bytes)
    mock_s3.upload_fileobj = Mock()

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
    }

    # Run task
    result = await process_inbound_email_task(mock_context, inbound_email_id=email.id)

    # Verify result
    assert result["status"] == "processed"
    assert result["from"] == "sender@example.com"
    assert result["subject"] == "Test Contract Submission"

    # Verify database updates
    await db_session.refresh(email)
    assert email.state == InboundEmailState.PROCESSED
    assert email.from_email == "sender@example.com"
    assert email.subject == "Test Contract Submission"
    assert email.processed_at is not None
    assert email.error_message is None


async def test_task_extracts_attachments(
    db_session: AsyncSession,
):
    """Test task extracts and uploads attachment to S3."""
    # Create email with attachment
    msg = EmailMessage()
    msg["From"] = "client@agency.com"
    msg["To"] = "contracts@tryarive.com"
    msg["Subject"] = "Contract with attachment"
    msg.set_content("Please find the contract attached.")
    msg.add_attachment(
        b"%PDF-1.4\n%fake pdf content for testing",
        maintype="application",
        subtype="pdf",
        filename="contract.pdf",
    )

    email = await InboundEmailFactory.create_async(
        session=db_session,
        state=InboundEmailState.RECEIVED,
    )
    await db_session.commit()

    # Mock S3 client
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(return_value=msg.as_bytes())
    mock_s3.upload_fileobj = Mock()

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
    }

    # Run task
    result = await process_inbound_email_task(mock_context, inbound_email_id=email.id)

    # Verify attachment was uploaded
    assert mock_s3.upload_fileobj.call_count == 1
    assert result["attachment_count"] == 1

    # Verify attachment metadata
    await db_session.refresh(email)
    assert email.attachments_json is not None
    assert len(email.attachments_json["attachments"]) == 1
    attachment = email.attachments_json["attachments"][0]
    assert attachment["filename"] == "contract.pdf"
    assert attachment["content_type"] == "application/pdf"


async def test_task_handles_s3_error(
    db_session: AsyncSession,
):
    """Test task handles S3 fetch errors gracefully."""
    email = await InboundEmailFactory.create_async(
        session=db_session,
        state=InboundEmailState.RECEIVED,
    )
    await db_session.commit()

    # Mock S3 client to raise error
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(side_effect=Exception("S3 bucket not found"))

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
    }

    # Run task - should raise exception
    try:
        await process_inbound_email_task(mock_context, inbound_email_id=email.id)
    except Exception:
        pass  # Expected to raise

    # Verify error state
    await db_session.refresh(email)
    assert email.state == InboundEmailState.FAILED
    assert email.error_message == "S3 bucket not found"
