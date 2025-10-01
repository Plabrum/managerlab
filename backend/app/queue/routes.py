"""Queue demonstration routes."""

import time
from litestar import Controller, post
from litestar.response import Response
from litestar_saq import TaskQueues
from typing import TypedDict


class EnqueueResponse(TypedDict):
    """Response for task enqueue endpoint."""

    job_id: str
    queue: str
    status: str


class QueueController(Controller):
    """Controller for queue demonstrations."""

    path = "/queue"
    tags = ["queue"]

    @post("/example")
    async def enqueue_example(
        self, task_queues: TaskQueues, message: str
    ) -> Response[EnqueueResponse]:
        """
        Enqueue an example task for processing.

        Args:
            task_queues: SAQ task queues dependency injected by Litestar
            message: Message to process in the background

        Returns:
            Job details
        """
        queue = task_queues.get("default")
        job = await queue.enqueue("example_task", message=message)
        return Response(
            content={
                "job_id": job.id,
                "queue": job.queue,
                "status": "queued",
            }
        )

    @post("/email")
    async def enqueue_email(
        self, task_queues: TaskQueues, to: str, subject: str, email_body: str
    ) -> Response[EnqueueResponse]:
        """
        Enqueue an email to be sent asynchronously.

        Args:
            task_queues: SAQ task queues dependency
            to: Email recipient
            subject: Email subject
            email_body: Email body content

        Returns:
            Job details
        """
        queue = task_queues.get("default")
        job = await queue.enqueue(
            "send_email_task", to=to, subject=subject, body=email_body
        )
        return Response(
            content={
                "job_id": job.id,
                "queue": job.queue,
                "status": "queued",
            }
        )

    @post("/delayed")
    async def enqueue_delayed(
        self, task_queues: TaskQueues, message: str, delay_seconds: int = 10
    ) -> Response[EnqueueResponse]:
        """
        Enqueue a task to be processed after a delay.

        Args:
            task_queues: SAQ task queues dependency
            message: Message to process
            delay_seconds: Delay in seconds before processing

        Returns:
            Job details
        """
        queue = task_queues.get("default")
        scheduled_time = time.time() + delay_seconds
        job = await queue.enqueue(
            "example_task", message=message, scheduled=scheduled_time
        )
        return Response(
            content={
                "job_id": job.id,
                "queue": job.queue,
                "status": f"scheduled in {delay_seconds}s",
            }
        )


queue_router = QueueController
