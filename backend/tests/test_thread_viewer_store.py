"""Unit tests for ThreadViewerStore."""

import pytest
from litestar.stores.memory import MemoryStore

from app.threads.services import ThreadViewerStore


class TestThreadViewerStore:
    """High-value integration tests for ThreadViewerStore."""

    @pytest.mark.asyncio
    async def test_add_and_remove_viewers_workflow(
        self, memory_store: MemoryStore
    ) -> None:
        """Test adding and removing viewers with state verification at each step."""
        store = ThreadViewerStore(store=memory_store)
        thread_id = 1

        # Initially, thread should have no viewers
        viewers = await store.get_viewers(thread_id)
        assert viewers == set()

        # Add first viewer
        await store.add_viewer(thread_id, 101)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101}

        # Add second viewer
        await store.add_viewer(thread_id, 102)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101, 102}

        # Add third viewer
        await store.add_viewer(thread_id, 103)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101, 102, 103}

        # Add duplicate viewer (should not create duplicate)
        await store.add_viewer(thread_id, 101)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101, 102, 103}
        assert len(viewers) == 3

        # Remove one viewer
        await store.remove_viewer(thread_id, 102)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101, 103}

        # Remove another viewer
        await store.remove_viewer(thread_id, 101)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {103}

        # Remove last viewer
        await store.remove_viewer(thread_id, 103)
        viewers = await store.get_viewers(thread_id)
        assert viewers == set()

    @pytest.mark.asyncio
    async def test_edge_cases_and_graceful_handling(
        self, memory_store: MemoryStore
    ) -> None:
        """Test edge cases like removing non-existent viewers."""
        store = ThreadViewerStore(store=memory_store)
        thread_id = 1

        # Remove viewer from empty thread (should not error)
        await store.remove_viewer(thread_id, 999)
        viewers = await store.get_viewers(thread_id)
        assert viewers == set()

        # Add a viewer
        await store.add_viewer(thread_id, 101)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101}

        # Remove non-existent viewer (should not error, should not affect existing)
        await store.remove_viewer(thread_id, 999)
        viewers = await store.get_viewers(thread_id)
        assert viewers == {101}

    @pytest.mark.asyncio
    async def test_simultaneous_threads(self, memory_store: MemoryStore) -> None:
        """Test that multiple threads maintain independent viewer sets."""
        store = ThreadViewerStore(store=memory_store)

        # Add viewers to thread 1
        await store.add_viewer(1, 101)
        await store.add_viewer(1, 102)

        # Add viewers to thread 2
        await store.add_viewer(2, 201)
        await store.add_viewer(2, 202)

        # Add viewers to thread 3
        await store.add_viewer(3, 301)

        # Verify all threads have independent viewer sets
        assert await store.get_viewers(1) == {101, 102}
        assert await store.get_viewers(2) == {201, 202}
        assert await store.get_viewers(3) == {301}

        # Remove viewer from thread 2
        await store.remove_viewer(2, 201)

        # Verify thread 2 is updated but threads 1 and 3 are unchanged
        assert await store.get_viewers(1) == {101, 102}
        assert await store.get_viewers(2) == {202}
        assert await store.get_viewers(3) == {301}

        # Clear thread 1 completely
        await store.remove_viewer(1, 101)
        await store.remove_viewer(1, 102)

        # Verify thread 1 is empty but other threads are unchanged
        assert await store.get_viewers(1) == set()
        assert await store.get_viewers(2) == {202}
        assert await store.get_viewers(3) == {301}
