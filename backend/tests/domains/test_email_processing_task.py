"""Smoke tests for inbound email processing task."""

from email.message import EmailMessage
from unittest.mock import Mock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.emails.models import InboundEmail
from app.emails.tasks import process_inbound_email_task


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

    # Mock S3 client
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(return_value=email_bytes)
    mock_s3.upload_fileobj = Mock()

    # Create mock context (with mock job for task_id)
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-123"
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
    }

    # Run task with bucket and key
    result = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        key="emails/test-email.eml",
    )

    # Verify result
    assert result["status"] == "processed"
    assert result["from"] == "sender@example.com"
    assert result["subject"] == "Test Contract Submission"

    # Verify database record was created
    stmt = select(InboundEmail).where(InboundEmail.s3_key == "emails/test-email.eml")
    result_db = await db_session.execute(stmt)
    email = result_db.scalar_one()

    assert email.task_id == "test-task-id-123"
    assert email.s3_bucket == "test-inbound-emails-bucket"
    assert email.s3_key == "emails/test-email.eml"
    assert email.from_email == "sender@example.com"
    assert email.subject == "Test Contract Submission"
    assert email.processed_at is not None


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

    # Mock S3 client
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(return_value=msg.as_bytes())
    mock_s3.upload_fileobj = Mock()

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-456"
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
    }

    # Run task with bucket and key
    result = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        key="emails/test-email-with-attachment.eml",
    )

    # Verify attachment was uploaded
    assert mock_s3.upload_fileobj.call_count == 1
    assert result["attachment_count"] == 1

    # Verify database record and attachment metadata
    stmt = select(InboundEmail).where(InboundEmail.s3_key == "emails/test-email-with-attachment.eml")
    result_db = await db_session.execute(stmt)
    email = result_db.scalar_one()

    assert email.attachments_json is not None
    assert len(email.attachments_json["attachments"]) == 1
    attachment = email.attachments_json["attachments"][0]
    assert attachment["filename"] == "contract.pdf"
    assert attachment["content_type"] == "application/pdf"


async def test_task_handles_s3_error(
    db_session: AsyncSession,
):
    """Test task handles S3 fetch errors gracefully."""
    # Mock S3 client to raise error
    mock_s3 = Mock()
    mock_s3.get_file_bytes = Mock(side_effect=Exception("S3 bucket not found"))

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-789"
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
    }

    # Run task - should raise exception
    try:
        await process_inbound_email_task(
            mock_context,
            bucket="test-inbound-emails-bucket",
            key="emails/test-email-error.eml",
        )
    except Exception:
        pass  # Expected to raise

    # Verify record was created with task_id before failure
    stmt = select(InboundEmail).where(InboundEmail.s3_key == "emails/test-email-error.eml")
    result_db = await db_session.execute(stmt)
    email = result_db.scalar_one()

    assert email.task_id == "test-task-id-789"
    # Error details stored in SAQ task, not on email record
