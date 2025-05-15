"""Tests for the position module."""

import pytest
from typing import List, Optional

from common.core.position import (
    Position,
    LineColumnPosition,
    StructuredPosition,
    LineBasedContentProtocol,
    StructuredContentProtocol,
    create_position,
)


class MockLineBasedContent(LineBasedContentProtocol):
    """Mock implementation of LineBasedContentProtocol for testing."""

    def __init__(self, content: str = ""):
        self.lines = content.split("\n") if content else [""]

    def get_content(self) -> str:
        return "\n".join(self.lines)

    def get_line(self, line_number: int) -> str:
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        raise IndexError(f"Line number {line_number} out of range")

    def get_line_count(self) -> int:
        return len(self.lines)


class MockSegment:
    """Mock segment for structured content testing."""

    def __init__(self, content: str):
        self.content = content


class MockSection:
    """Mock section for structured content testing."""

    def __init__(self, title: str, segments: List[str] = None):
        self.title = title
        self.segments = [MockSegment(text) for text in (segments or [])]


class MockStructuredContent(StructuredContentProtocol):
    """Mock implementation of StructuredContentProtocol for testing."""

    def __init__(self):
        self.sections = []

    def get_content(self) -> str:
        result = []
        for section in self.sections:
            section_text = [f"# {section.title}"]
            for segment in section.segments:
                section_text.append(segment.content)
            result.append("\n".join(section_text))
        return "\n\n".join(result)

    def add_section(self, title: str, segments: List[str] = None) -> MockSection:
        section = MockSection(title, segments)
        self.sections.append(section)
        return section

    def get_section(self, index: int) -> Optional[MockSection]:
        if 0 <= index < len(self.sections):
            return self.sections[index]
        return None

    def get_section_count(self) -> int:
        return len(self.sections)

    def get_segment(
        self, section_index: int, segment_index: int
    ) -> Optional[MockSegment]:
        section = self.get_section(section_index)
        if section and 0 <= segment_index < len(section.segments):
            return section.segments[segment_index]
        return None

    def get_segment_count(self, section_index: int) -> int:
        section = self.get_section(section_index)
        return len(section.segments) if section else 0


class TestLineColumnPosition:
    """Tests for LineColumnPosition."""

    def test_initialization(self):
        """Test that a LineColumnPosition can be initialized."""
        pos = LineColumnPosition(line=1, column=2)
        assert pos.line == 1
        assert pos.column == 2

    def test_get_position(self):
        """Test getting the position as a tuple."""
        pos = LineColumnPosition(line=1, column=2)
        assert pos.get_position() == (1, 2)

    def test_set_position(self):
        """Test setting the position."""
        content = MockLineBasedContent("Line 1\nLine 2\nLine 3")
        pos = LineColumnPosition(content=content)

        pos.set_position(1, 3)
        assert pos.line == 1
        assert pos.column == 3

        # Test bounds checking
        with pytest.raises(IndexError):
            pos.set_position(5, 0)  # Invalid line

        with pytest.raises(IndexError):
            pos.set_position(1, 10)  # Invalid column

    def test_move_methods(self):
        """Test the movement methods."""
        content = MockLineBasedContent("Line 1\nLine 2\nLine 3")
        pos = LineColumnPosition(content=content)

        # Test move_up and move_down
        pos.set_position(1, 2)
        pos.move_up()
        assert pos.get_position() == (0, 2)

        pos.move_down(2)
        assert pos.get_position() == (2, 2)

        # Test move_left and move_right
        pos.set_position(1, 2)
        pos.move_left()
        assert pos.get_position() == (1, 1)

        pos.move_right(3)
        assert pos.get_position() == (1, 4)

        # Test crossing lines
        pos.set_position(1, 0)
        pos.move_left()
        assert pos.get_position() == (0, 6)  # End of previous line

        pos.set_position(0, 6)
        pos.move_right()
        assert pos.get_position() == (1, 0)  # Start of next line

    def test_move_to_methods(self):
        """Test the move_to_* methods."""
        content = MockLineBasedContent("Line 1\nLine 2\nLine 3")
        pos = LineColumnPosition(content=content)

        pos.set_position(1, 3)

        pos.move_to_line_start()
        assert pos.get_position() == (1, 0)

        pos.move_to_line_end()
        assert pos.get_position() == (1, 6)

        pos.move_to_content_start()
        assert pos.get_position() == (0, 0)

        pos.move_to_content_end()
        assert pos.get_position() == (2, 6)

    def test_comparison_methods(self):
        """Test comparison methods."""
        pos1 = LineColumnPosition(line=1, column=2)
        pos2 = LineColumnPosition(line=1, column=2)
        pos3 = LineColumnPosition(line=1, column=3)
        pos4 = LineColumnPosition(line=2, column=0)

        assert pos1.equals(pos2)
        assert not pos1.equals(pos3)

        assert pos1.before(pos3)
        assert pos1.before(pos4)
        assert not pos4.before(pos1)

        assert pos3.after(pos1)
        assert pos4.after(pos1)
        assert not pos1.after(pos4)


class TestStructuredPosition:
    """Tests for StructuredPosition."""

    def test_initialization(self):
        """Test that a StructuredPosition can be initialized."""
        pos = StructuredPosition(section_index=1, segment_index=2, offset_in_segment=3)
        assert pos.section_index == 1
        assert pos.segment_index == 2
        assert pos.offset_in_segment == 3

    def test_get_position(self):
        """Test getting the position as a tuple."""
        pos = StructuredPosition(section_index=1, segment_index=2, offset_in_segment=3)
        assert pos.get_position() == (1, 2, 3)

    def test_set_position(self):
        """Test setting the position."""
        content = MockStructuredContent()
        content.add_section("Section 1", ["Segment 1", "Segment 2"])
        content.add_section("Section 2", ["Segment 3", "Segment 4"])

        pos = StructuredPosition(content=content)

        pos.set_position(1, 0, 3)
        assert pos.section_index == 1
        assert pos.segment_index == 0
        assert pos.offset_in_segment == 3

        # Test bounds checking
        with pytest.raises(IndexError):
            pos.set_position(2, 0, 0)  # Invalid section

        with pytest.raises(IndexError):
            pos.set_position(1, 2, 0)  # Invalid segment

        with pytest.raises(IndexError):
            pos.set_position(1, 0, 20)  # Invalid offset

    def test_move_methods(self):
        """Test the movement methods."""
        content = MockStructuredContent()
        content.add_section("Section 1", ["Segment 1", "Segment 2"])
        content.add_section("Section 2", ["Segment 3", "Segment 4"])

        pos = StructuredPosition(content=content)

        # Test move_to_next_segment and move_to_previous_segment
        pos.set_position(0, 0, 0)
        assert pos.move_to_next_segment()
        assert pos.get_position() == (0, 1, 0)

        assert pos.move_to_next_segment()
        assert pos.get_position() == (1, 0, 0)

        assert pos.move_to_previous_segment()
        assert pos.get_position() == (0, 1, 9)  # "Segment 2" length

        # Test move_to_next_section and move_to_previous_section
        pos.set_position(0, 0, 0)
        assert pos.move_to_next_section()
        assert pos.get_position() == (1, 0, 0)

        assert pos.move_to_previous_section()
        assert pos.get_position() == (0, 0, 0)

    def test_move_to_methods(self):
        """Test the move_to_* methods."""
        content = MockStructuredContent()
        content.add_section("Section 1", ["Segment 1", "Segment 2"])
        content.add_section("Section 2", ["Segment 3", "Segment 4"])

        pos = StructuredPosition(content=content)

        pos.set_position(1, 1, 3)

        pos.move_to_segment_start()
        assert pos.get_position() == (1, 1, 0)

        pos.move_to_segment_end()
        assert pos.get_position() == (1, 1, 9)  # "Segment 4" length

        pos.move_to_section_start()
        assert pos.get_position() == (1, 0, 0)

        pos.move_to_section_end()
        assert pos.get_position() == (1, 1, 9)

        pos.move_to_content_start()
        assert pos.get_position() == (0, 0, 0)

        pos.move_to_content_end()
        assert pos.get_position() == (1, 1, 9)

    def test_comparison_methods(self):
        """Test comparison methods."""
        pos1 = StructuredPosition(section_index=1, segment_index=2, offset_in_segment=3)
        pos2 = StructuredPosition(section_index=1, segment_index=2, offset_in_segment=3)
        pos3 = StructuredPosition(section_index=1, segment_index=2, offset_in_segment=4)
        pos4 = StructuredPosition(section_index=1, segment_index=3, offset_in_segment=0)
        pos5 = StructuredPosition(section_index=2, segment_index=0, offset_in_segment=0)

        assert pos1.equals(pos2)
        assert not pos1.equals(pos3)

        assert pos1.before(pos3)
        assert pos1.before(pos4)
        assert pos1.before(pos5)
        assert not pos5.before(pos1)

        assert pos3.after(pos1)
        assert pos4.after(pos1)
        assert pos5.after(pos1)
        assert not pos1.after(pos5)


def test_create_position():
    """Test the create_position factory function."""
    line_content = MockLineBasedContent("Line 1\nLine 2")
    pos1 = create_position(line_content)
    assert isinstance(pos1, LineColumnPosition)

    struct_content = MockStructuredContent()
    struct_content.add_section("Section 1", ["Segment 1"])
    pos2 = create_position(struct_content)
    assert isinstance(pos2, StructuredPosition)

    # Test with invalid content type
    class InvalidContent:
        pass

    with pytest.raises(TypeError):
        create_position(InvalidContent())
