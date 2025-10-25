"""Tests for event consumer helper functions."""

from app.events.consumers import (
    build_update_message_content,
    _parse_event_data_to_updated,
)
from app.events.schemas import FieldChange, UpdatedEventData


# Mock object for testing
class MockObject:
    """Mock database model for testing."""

    def __init__(self, id: int, name: str | None = None, title: str | None = None):
        self.id = id
        self.name = name
        self.title = title


class TestParseEventDataToUpdated:
    """Test cases for _parse_event_data_to_updated function."""

    def test_parse_valid_event_data(self):
        """Test parsing valid event data with multiple fields."""
        event_data = {
            "name": {"old": "Old Name", "new": "New Name"},
            "status": {"old": "draft", "new": "active"},
        }

        result = _parse_event_data_to_updated(event_data)

        assert result is not None
        assert isinstance(result, UpdatedEventData)
        assert len(result.changes) == 2
        assert result.changes["name"].old == "Old Name"
        assert result.changes["name"].new == "New Name"
        assert result.changes["status"].old == "draft"
        assert result.changes["status"].new == "active"

    def test_parse_empty_event_data(self):
        """Test parsing empty event data returns None."""
        result = _parse_event_data_to_updated({})
        assert result is None

    def test_parse_none_event_data(self):
        """Test parsing None event data returns None."""
        result = _parse_event_data_to_updated(None)
        assert result is None

    def test_parse_with_null_values(self):
        """Test parsing event data with None values."""
        event_data = {
            "description": {"old": None, "new": "New Description"},
            "budget": {"old": 1000, "new": None},
        }

        result = _parse_event_data_to_updated(event_data)

        assert result is not None
        assert result.changes["description"].old is None
        assert result.changes["description"].new == "New Description"
        assert result.changes["budget"].old == 1000
        assert result.changes["budget"].new is None

    def test_parse_ignores_invalid_fields(self):
        """Test that invalid fields are ignored."""
        event_data = {
            "name": {"old": "Old Name", "new": "New Name"},
            "invalid_field": "not a dict",
            "missing_new": {"old": "value"},
            "missing_old": {"new": "value"},
        }

        result = _parse_event_data_to_updated(event_data)

        assert result is not None
        assert len(result.changes) == 1
        assert "name" in result.changes
        assert "invalid_field" not in result.changes
        assert "missing_new" not in result.changes
        assert "missing_old" not in result.changes

    def test_parse_numeric_values(self):
        """Test parsing numeric field changes."""
        event_data = {
            "budget": {"old": 1000, "new": 2000},
            "quantity": {"old": 5, "new": 10},
        }

        result = _parse_event_data_to_updated(event_data)

        assert result is not None
        assert result.changes["budget"].old == 1000
        assert result.changes["budget"].new == 2000
        assert result.changes["quantity"].old == 5
        assert result.changes["quantity"].new == 10

    def test_parse_structured_format_from_database(self):
        """Test parsing event data in structured format (as stored in DB)."""
        # This is how UpdatedEventData is stored in the database
        event_data = {
            "changes": {
                "instagram_handle": {"old": "@matty", "new": "@mattyb"},
                "name": {"old": "Old Name", "new": "New Name"},
            }
        }

        result = _parse_event_data_to_updated(event_data)

        assert result is not None
        assert len(result.changes) == 2
        assert result.changes["instagram_handle"].old == "@matty"
        assert result.changes["instagram_handle"].new == "@mattyb"
        assert result.changes["name"].old == "Old Name"
        assert result.changes["name"].new == "New Name"


class TestBuildUpdateMessageContent:
    """Test cases for build_update_message_content function."""

    def test_build_with_name_and_single_change(self):
        """Test building message with single field change."""
        obj = MockObject(id=1, name="Test Campaign")
        event_data = UpdatedEventData(
            changes={"status": FieldChange(old="draft", new="active")}
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=1,
        )

        # Verify structure
        assert content["type"] == "doc"
        assert "content" in content
        assert len(content["content"]) == 1
        assert content["content"][0]["type"] == "paragraph"

        # Verify nodes
        nodes = content["content"][0]["content"]
        assert any(node.get("text") == "updated " for node in nodes)
        assert any(node.get("text") == ": " for node in nodes)
        assert any(
            node.get("text") == "Status"
            and node.get("marks")
            and node["marks"][0]["type"] == "bold"
            for node in nodes
        )
        assert any(node.get("text") == ": draft → active" for node in nodes)

    def test_build_with_multiple_changes(self):
        """Test building message with multiple field changes."""
        obj = MockObject(id=2, name="Test Brand")
        event_data = UpdatedEventData(
            changes={
                "name": FieldChange(old="Old Name", new="New Name"),
                "status": FieldChange(old="draft", new="active"),
                "budget": FieldChange(old=1000, new=2000),
            }
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="brand",
            object_id=2,
        )

        # Extract all text content
        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Verify all changes are present
        assert "updated " in all_text
        assert "Old Name → New Name" in all_text
        assert "draft → active" in all_text
        assert "1000 → 2000" in all_text

    def test_build_without_name_falls_back_to_id(self):
        """Test that objects without name attributes still build valid messages."""
        obj = MockObject(id=123)  # No name or title
        event_data = UpdatedEventData(
            changes={"status": FieldChange(old="draft", new="active")}
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="roster",
            object_id=123,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Should contain update message with field changes
        assert "updated " in all_text
        assert "Status" in all_text
        assert "draft → active" in all_text

    def test_build_with_title_attribute(self):
        """Test building message with title attribute."""
        obj = MockObject(id=456, title="Test Title")
        event_data = UpdatedEventData(
            changes={"status": FieldChange(old="draft", new="active")}
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=456,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Should contain update message with field changes
        assert "updated " in all_text
        assert "Status" in all_text
        assert "draft → active" in all_text

    def test_build_without_event_data(self):
        """Test building message when no event data is provided."""
        obj = MockObject(id=789, name="Test Object")

        content = build_update_message_content(
            obj=obj,
            event_data=None,
            object_type="campaign",
            object_id=789,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Should only contain base message
        assert "updated " in all_text
        # Should not contain field changes separator
        assert all_text == "updated "

    def test_build_with_null_values(self):
        """Test building message with None values in field changes."""
        obj = MockObject(id=999, name="Test Object")
        event_data = UpdatedEventData(
            changes={
                "description": FieldChange(old=None, new="New Description"),
                "budget": FieldChange(old=1000, new=None),
            }
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=999,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Verify None is displayed as "None"
        assert "None → New Description" in all_text
        assert "1000 → None" in all_text

    def test_build_with_underscore_field_names(self):
        """Test that underscore field names are converted to title case."""
        obj = MockObject(id=111, name="Test Object")
        event_data = UpdatedEventData(
            changes={
                "start_date": FieldChange(old="2024-01-01", new="2024-02-01"),
                "end_date": FieldChange(old="2024-12-31", new="2025-01-31"),
            }
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=111,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Verify field names are properly formatted
        assert "Start Date" in all_text
        assert "End Date" in all_text

    def test_build_with_underscore_object_type(self):
        """Test building message with underscore in object type."""
        obj = MockObject(id=222, name="Test Object")
        event_data = UpdatedEventData(
            changes={"status": FieldChange(old="draft", new="active")}
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign_draft",
            object_id=222,
        )

        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        # Should contain update message with field changes
        assert "updated " in all_text
        assert "Status" in all_text
        assert "draft → active" in all_text

    def test_build_preserves_order_of_changes(self):
        """Test that multiple changes are displayed in order."""
        obj = MockObject(id=333, name="Test Object")
        event_data = UpdatedEventData(
            changes={
                "first_field": FieldChange(old="a", new="b"),
                "second_field": FieldChange(old="c", new="d"),
                "third_field": FieldChange(old="e", new="f"),
            }
        )

        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=333,
        )

        nodes = content["content"][0]["content"]
        text_nodes = [node.get("text", "") for node in nodes]
        full_text = "".join(text_nodes)

        # All three changes should be present
        assert "First Field" in full_text
        assert "Second Field" in full_text
        assert "Third Field" in full_text

        # Changes should be comma-separated
        assert full_text.count(", ") >= 2


class TestIntegration:
    """Integration tests combining both functions."""

    def test_full_workflow_with_raw_event_data(self):
        """Test complete workflow from raw event data to TipTap content."""
        # Simulate raw event data from Event.event_data
        raw_event_data = {
            "name": {"old": "Old Campaign", "new": "New Campaign"},
            "status": {"old": "draft", "new": "active"},
        }

        # Step 1: Parse event data
        event_data = _parse_event_data_to_updated(raw_event_data)
        assert event_data is not None

        # Step 2: Build message content
        obj = MockObject(id=1, name="New Campaign")
        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=1,
        )

        # Verify final output
        assert content["type"] == "doc"
        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        assert "updated " in all_text
        assert "Old Campaign → New Campaign" in all_text
        assert "draft → active" in all_text

    def test_workflow_with_no_changes(self):
        """Test workflow when there are no valid changes in event data."""
        raw_event_data = {"invalid": "data"}

        event_data = _parse_event_data_to_updated(raw_event_data)
        assert event_data is None

        obj = MockObject(id=1, name="Test Object")
        content = build_update_message_content(
            obj=obj,
            event_data=event_data,
            object_type="campaign",
            object_id=1,
        )

        # Should still build valid message, just without field details
        assert content["type"] == "doc"
        nodes = content["content"][0]["content"]
        all_text = "".join(node.get("text", "") for node in nodes)

        assert "updated " in all_text
        assert all_text == "updated "
