"""
Meetings Module Library.

Provides utilities for transcript processing and Google Docs integration.

Usage:
    from meetings.lib.google_docs import GoogleDocsClient
    from meetings.lib.transcription_parser import TranscriptionParser
"""

from .google_docs import GoogleDocsClient, DocContent
from .transcription_parser import (
    TranscriptionParser,
    ParsedTranscript,
    TranscriptLine,
    ActionItem,
    Decision,
    Question,
)

__all__ = [
    "GoogleDocsClient",
    "DocContent",
    "TranscriptionParser",
    "ParsedTranscript",
    "TranscriptLine",
    "ActionItem",
    "Decision",
    "Question",
]
