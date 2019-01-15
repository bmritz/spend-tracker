"""Utility helper functions for parsing text."""
import re


def iter_sections(document, section_delimiter_pattern):
    """Yields each section of a document, as separated by lines that match section_delimiter_pattern.

    Args:
        document(string): The document to iterate over
        section_delimiter_pattern(string): Regex pattern to search for to delimit sections.

    """
    key = None
    lines = []
    for line in document.split("\n"):
        if re.search(section_delimiter_pattern, line.strip()):
            if key:
                yield key, "\n".join(lines)
            key = line
            lines = []
        else:
            lines.append(line)
    if key:
        yield key, "\n".join(lines)
