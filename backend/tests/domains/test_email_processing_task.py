"""Smoke tests for inbound email processing task."""

from email.message import EmailMessage
from unittest.mock import AsyncMock, Mock

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
    mock_s3.get_file_bytes_from_bucket = Mock(return_value=email_bytes)
    mock_s3.upload_fileobj = Mock()

    # Create mock context (with mock job for task_id)
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-123"
    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
        "queue": mock_queue,
    }

    # Run task with bucket and s3_key
    result = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        s3_key="emails/test-email.eml",
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
    mock_s3.get_file_bytes_from_bucket = Mock(return_value=msg.as_bytes())
    mock_s3.upload_fileobj = Mock()

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-456"
    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
        "queue": mock_queue,
    }

    # Run task with bucket and s3_key
    result = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        s3_key="emails/test-email-with-attachment.eml",
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

    # Verify campaign creation task was enqueued for the attachment
    assert mock_queue.enqueue.call_count == 1
    call_args = mock_queue.enqueue.call_args
    assert call_args[0][0] == "create_campaign_from_attachment_task"
    assert "inbound_email_id" in call_args[1]
    assert call_args[1]["attachment_index"] == 0


async def test_task_handles_s3_error(
    db_session: AsyncSession,
):
    """Test task handles S3 fetch errors gracefully - no orphaned records."""
    # Mock S3 client to raise error
    mock_s3 = Mock()
    mock_s3.get_file_bytes_from_bucket = Mock(side_effect=Exception("S3 bucket not found"))

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-789"
    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
        "queue": mock_queue,
    }

    # Run task - should raise exception
    task_raised = False
    try:
        await process_inbound_email_task(
            mock_context,
            bucket="test-inbound-emails-bucket",
            s3_key="emails/test-email-error.eml",
        )
    except Exception:
        task_raised = True

    assert task_raised, "Task should have raised an exception"

    # Verify NO record was created (transaction pattern prevents orphaned records)
    stmt = select(InboundEmail).where(InboundEmail.s3_key == "emails/test-email-error.eml")
    result_db = await db_session.execute(stmt)
    email = result_db.scalar_one_or_none()

    assert email is None, "No database record should exist when S3 fetch fails"
    # Error is captured in SAQ task state, not in database


async def test_task_handles_duplicate_calls(
    db_session: AsyncSession,
):
    """Test task is idempotent - duplicate calls don't create duplicate records."""
    # Create sample email
    msg = EmailMessage()
    msg["From"] = "duplicate@example.com"
    msg["To"] = "contracts@tryarive.com"
    msg["Subject"] = "Duplicate Test Email"
    msg["Date"] = "Mon, 13 Nov 2023 11:00:00 -0500"
    msg["Message-ID"] = "<duplicate123@mail.example.com>"
    msg.set_content("This email will be processed twice.")
    email_bytes = msg.as_bytes()

    # Mock S3 client
    mock_s3 = Mock()
    mock_s3.get_file_bytes_from_bucket = Mock(return_value=email_bytes)
    mock_s3.upload_fileobj = Mock()

    # Create mock context
    sessionmaker = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    mock_job = Mock()
    mock_job.key = "test-task-id-duplicate"
    mock_queue = Mock()
    mock_queue.enqueue = AsyncMock()
    mock_context = {
        "db_sessionmaker": sessionmaker,
        "s3_client": mock_s3,
        "job": mock_job,
        "queue": mock_queue,
    }

    # First call - should process normally
    result1 = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        s3_key="emails/duplicate-email.eml",
    )

    assert result1["status"] == "processed"
    assert result1["from"] == "duplicate@example.com"
    first_id = result1["inbound_email_id"]

    # Second call - should detect duplicate and return early (on_conflict_do_nothing)
    result2 = await process_inbound_email_task(
        mock_context,
        bucket="test-inbound-emails-bucket",
        s3_key="emails/duplicate-email.eml",
    )

    assert result2["status"] == "processed"  # Same status as first call
    assert result2["inbound_email_id"] == first_id  # Same ID
    assert result2["from"] == "duplicate@example.com"

    # Verify only ONE record exists in database
    stmt = select(InboundEmail).where(InboundEmail.s3_key == "emails/duplicate-email.eml")
    result_db = await db_session.execute(stmt)
    emails = result_db.scalars().all()

    assert len(emails) == 1, "Should have exactly one record despite duplicate calls"
    assert emails[0].id == first_id
