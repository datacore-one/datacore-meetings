"""
Transcription Parser for Meetings Module.

Parse meeting transcripts and extract structured data:
- Action items with assignees
- Decisions made
- Questions raised/resolved

Supports multiple transcript formats:
- Google Meet auto-transcripts (timestamped, speaker-labeled)
- Granola exports (.md)
- Plain text transcripts

Usage:
    from meetings.lib.transcription_parser import TranscriptionParser

    parser = TranscriptionParser()
    result = parser.parse(transcript_content)

    for action in result.action_items:
        print(f"Action: {action.description} -> @{action.assignee}")
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class TranscriptLine:
    """Single line from a transcript."""
    timestamp: Optional[str]  # e.g., "00:01:15"
    speaker: str
    text: str
    line_number: int = 0


@dataclass
class ActionItem:
    """Extracted action item."""
    description: str
    assignee: Optional[str]
    source_line: str
    speaker: str
    confidence: float  # 0-1
    deadline: Optional[str] = None  # e.g., "by Friday"


@dataclass
class Decision:
    """Extracted decision."""
    description: str
    context: str
    source_line: str
    speaker: str
    confidence: float


@dataclass
class Question:
    """Question raised or referenced."""
    text: str
    speaker: str
    source_line: str
    is_resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class ParsedTranscript:
    """Complete parsed transcript result."""
    lines: List[TranscriptLine]
    action_items: List[ActionItem]
    decisions: List[Decision]
    questions_raised: List[Question]
    speakers: List[str]
    duration_estimate: Optional[int] = None  # minutes
    format_detected: str = "unknown"

    @property
    def summary_stats(self) -> dict:
        """Get summary statistics."""
        return {
            "total_lines": len(self.lines),
            "speakers": len(self.speakers),
            "action_items": len(self.action_items),
            "decisions": len(self.decisions),
            "questions": len(self.questions_raised),
            "duration_minutes": self.duration_estimate,
        }


class TranscriptionParser:
    """Parse transcripts and extract structured data."""

    # === Action Item Patterns ===
    # Ordered by confidence (highest first)
    ACTION_PATTERNS = [
        # Explicit action items (confidence: 1.0)
        (r"(?:Action item|TODO|Task|AI):\s*(?P<action>.+)", 1.0, None),
        # @person will/should (confidence: 0.95)
        (r"@(?P<person>\w+)\s+(?:will|should|needs to|is going to)\s+(?P<action>.+)", 0.95, "person"),
        # Person will/should with explicit name (confidence: 0.9)
        (r"(?P<person>[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:will|should|needs to|is going to)\s+(?P<action>.+)", 0.85, "person"),
        # I'll/I will (confidence: 0.9) - speaker becomes assignee
        (r"(?:I'll|I will|I'm going to|I am going to)\s+(?P<action>.+)", 0.9, "speaker"),
        # Let's/We should (confidence: 0.6) - team action, needs assignment
        (r"(?:Let's|We should|We need to|We'll)\s+(?P<action>.+)", 0.6, None),
    ]

    # === Decision Patterns ===
    DECISION_PATTERNS = [
        # Explicit decision markers (confidence: 1.0)
        (r"(?:Decision|Decided):\s*(?P<decision>.+)", 1.0),
        # We decided/agreed (confidence: 0.95)
        (r"(?:We decided|We've decided|We agreed|It's agreed)\s+(?:that\s+|to\s+)?(?P<decision>.+)", 0.95),
        # The plan is/Going forward (confidence: 0.85)
        (r"(?:The plan is|Going forward|From now on)\s+(?P<decision>.+)", 0.85),
        # We'll go with/use (confidence: 0.8)
        (r"(?:We'll go with|We're going with|We'll use|Let's go with)\s+(?P<decision>.+)", 0.8),
        # So we're doing (confidence: 0.75)
        (r"(?:So we're doing|So we'll|So we will)\s+(?P<decision>.+)", 0.75),
    ]

    # === Question Patterns ===
    QUESTION_PATTERNS = [
        # Explicit question (ends with ?)
        r"(?P<question>[^.!?]*\?)",
        # "The question is" pattern
        r"(?:The question is|Question:)\s*(?P<question>[^.!?]+)",
        # "We need to figure out" pattern
        r"(?:We need to figure out|We should discuss)\s+(?P<question>[^.!?]+)",
    ]

    # === Deadline Patterns ===
    DEADLINE_PATTERNS = [
        r"by\s+(?P<deadline>(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))",
        r"by\s+(?P<deadline>(?:tomorrow|end of (?:day|week)|EOD|EOW))",
        r"by\s+(?P<deadline>(?:Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov)\s+\d{1,2})",
        r"(?:due|deadline)\s+(?P<deadline>.+?)(?:\.|,|$)",
    ]

    # === Google Meet Format ===
    # Format: [00:00:15] John Smith: Text goes here
    GOOGLE_MEET_PATTERN = re.compile(
        r'^\[?(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\]?\s*'
        r'(?P<speaker>[^:]+):\s*'
        r'(?P<text>.+)$'
    )

    # === Granola Format ===
    # Format: **Speaker Name**: Text or ## Speaker Name followed by text
    GRANOLA_SPEAKER_PATTERN = re.compile(
        r'^\*\*(?P<speaker>[^*]+)\*\*:\s*(?P<text>.+)$'
    )

    # === Gemini Notes Format ===
    # Format: "Notes by Gemini" with Summary, Details, Suggested next steps
    GEMINI_ACTION_PATTERN = re.compile(
        r'(?P<person>[A-Z][a-zčćžšđ]+(?:\s+[A-Z][a-zčćžšđ]+)?)\s+'
        r'(?:will|should|needs to|is going to)\s+'
        r'(?P<action>.+?)(?:\.|$)',
        re.IGNORECASE
    )

    def parse(self, content: str, format: str = "auto") -> ParsedTranscript:
        """Parse transcript content.

        Args:
            content: Raw transcript text
            format: "auto", "google_meet", "granola", or "plain"

        Returns:
            ParsedTranscript with extracted data
        """
        # Detect format if auto
        if format == "auto":
            format = self.detect_format(content)

        # Parse lines based on format
        if format == "google_meet":
            lines = self._parse_google_meet(content)
        elif format == "granola":
            lines = self._parse_granola(content)
        elif format == "gemini":
            lines = self._parse_gemini(content)
        else:
            lines = self._parse_plain(content)

        # Extract speakers
        speakers = list(set(line.speaker for line in lines if line.speaker))

        # Estimate duration from timestamps
        duration = self._estimate_duration(lines)

        # Extract action items
        action_items = self._extract_action_items(lines)

        # Extract decisions
        decisions = self._extract_decisions(lines)

        # Extract questions
        questions = self._extract_questions(lines)

        return ParsedTranscript(
            lines=lines,
            action_items=action_items,
            decisions=decisions,
            questions_raised=questions,
            speakers=speakers,
            duration_estimate=duration,
            format_detected=format,
        )

    def detect_format(self, content: str) -> str:
        """Auto-detect transcript format.

        Returns: "google_meet", "granola", "gemini", or "plain"
        """
        lines = content.strip().split('\n')[:30]  # Check first 30 lines
        content_lower = content.lower()

        # Check for Gemini notes format
        if 'notes by gemini' in content_lower or 'suggested next steps' in content_lower:
            return "gemini"

        google_meet_count = 0
        granola_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for Google Meet format: [00:00:15] Speaker: text
            if self.GOOGLE_MEET_PATTERN.match(line):
                google_meet_count += 1

            # Check for Granola format: **Speaker**: text
            if self.GRANOLA_SPEAKER_PATTERN.match(line):
                granola_count += 1

        # Determine format based on matches
        if google_meet_count >= 3:
            return "google_meet"
        elif granola_count >= 3:
            return "granola"
        else:
            return "plain"

    def _parse_google_meet(self, content: str) -> List[TranscriptLine]:
        """Parse Google Meet transcript format.

        Format: [00:00:15] John Smith: Text goes here
        """
        lines = []
        raw_lines = content.strip().split('\n')

        for i, raw_line in enumerate(raw_lines):
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            match = self.GOOGLE_MEET_PATTERN.match(raw_line)
            if match:
                lines.append(TranscriptLine(
                    timestamp=match.group('timestamp'),
                    speaker=match.group('speaker').strip(),
                    text=match.group('text').strip(),
                    line_number=i + 1,
                ))
            else:
                # Non-matching lines might be continuation
                if lines:
                    # Append to previous line
                    lines[-1].text += ' ' + raw_line
                else:
                    # Standalone line without speaker
                    lines.append(TranscriptLine(
                        timestamp=None,
                        speaker="Unknown",
                        text=raw_line,
                        line_number=i + 1,
                    ))

        return lines

    def _parse_granola(self, content: str) -> List[TranscriptLine]:
        """Parse Granola markdown export format.

        Format: **Speaker Name**: Text goes here
        """
        lines = []
        raw_lines = content.strip().split('\n')
        current_speaker = "Unknown"

        for i, raw_line in enumerate(raw_lines):
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith('#'):
                continue

            match = self.GRANOLA_SPEAKER_PATTERN.match(raw_line)
            if match:
                current_speaker = match.group('speaker').strip()
                text = match.group('text').strip()
                lines.append(TranscriptLine(
                    timestamp=None,
                    speaker=current_speaker,
                    text=text,
                    line_number=i + 1,
                ))
            elif raw_line.startswith('- ') or raw_line.startswith('* '):
                # Bullet points under a speaker
                lines.append(TranscriptLine(
                    timestamp=None,
                    speaker=current_speaker,
                    text=raw_line[2:].strip(),
                    line_number=i + 1,
                ))
            else:
                # Regular text, use current speaker
                lines.append(TranscriptLine(
                    timestamp=None,
                    speaker=current_speaker,
                    text=raw_line,
                    line_number=i + 1,
                ))

        return lines

    def _parse_gemini(self, content: str) -> List[TranscriptLine]:
        """Parse Gemini meeting notes format.

        Gemini notes have sections:
        - Summary
        - Details (with timestamps like (00:00:00))
        - Suggested next steps
        """
        lines = []
        raw_lines = content.strip().split('\n')

        current_section = "unknown"
        speakers_found = set()

        # First pass: extract all speaker names mentioned
        speaker_pattern = re.compile(
            r'([A-Z][a-zčćžšđ]+(?:\s+[A-Z][a-zčćžšđ]+)?)\s+'
            r'(?:and\s+)?([A-Z][a-zčćžšđ]+(?:\s+[A-Z][a-zčćžšđ]+)?)?'
            r'(?:\s+(?:discussed|mentioned|noted|confirmed|inquired|responded|brought up|covered|will|should))'
        )
        for raw_line in raw_lines:
            matches = speaker_pattern.findall(raw_line)
            for match in matches:
                if match[0] and match[0] not in ['The', 'They', 'This', 'That']:
                    speakers_found.add(match[0])
                if match[1] and match[1] not in ['The', 'They', 'This', 'That']:
                    speakers_found.add(match[1])

        current_speaker = list(speakers_found)[0] if speakers_found else "Unknown"

        for i, raw_line in enumerate(raw_lines):
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            # Detect section headers
            if raw_line.lower() == 'summary':
                current_section = "summary"
                continue
            elif raw_line.lower() == 'details':
                current_section = "details"
                continue
            elif raw_line.lower().startswith('suggested next steps'):
                current_section = "next_steps"
                continue
            elif raw_line.lower().startswith('notes length'):
                continue

            # Extract speaker mentions in details
            # Pattern: "Speaker Name discussed/mentioned/noted..."
            speaker_mention = re.match(
                r'^([A-Z][a-zčćžšđ]+(?:\s+[A-Z][a-zčćžšđ]+)?)\s+'
                r'(?:discussed|mentioned|noted|confirmed|inquired|responded|brought up|covered)',
                raw_line
            )
            if speaker_mention:
                current_speaker = speaker_mention.group(1)

            # Extract timestamp from Gemini format: (00:00:00)
            timestamp = None
            ts_match = re.search(r'\((\d{2}:\d{2}:\d{2})\)', raw_line)
            if ts_match:
                timestamp = ts_match.group(1)

            lines.append(TranscriptLine(
                timestamp=timestamp,
                speaker=current_speaker,
                text=raw_line,
                line_number=i + 1,
            ))

        return lines

    def _parse_plain(self, content: str) -> List[TranscriptLine]:
        """Parse plain text transcript (no specific format)."""
        lines = []
        raw_lines = content.strip().split('\n')

        for i, raw_line in enumerate(raw_lines):
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            # Try to detect speaker from "Name:" pattern
            speaker_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*:\s*(.+)$', raw_line)
            if speaker_match:
                lines.append(TranscriptLine(
                    timestamp=None,
                    speaker=speaker_match.group(1),
                    text=speaker_match.group(2),
                    line_number=i + 1,
                ))
            else:
                lines.append(TranscriptLine(
                    timestamp=None,
                    speaker="Unknown",
                    text=raw_line,
                    line_number=i + 1,
                ))

        return lines

    def _estimate_duration(self, lines: List[TranscriptLine]) -> Optional[int]:
        """Estimate meeting duration from timestamps."""
        timestamps = [line.timestamp for line in lines if line.timestamp]
        if len(timestamps) < 2:
            return None

        try:
            # Parse first and last timestamp
            first = self._parse_timestamp(timestamps[0])
            last = self._parse_timestamp(timestamps[-1])

            if first and last:
                duration_seconds = (last - first).total_seconds()
                return max(1, int(duration_seconds / 60))
        except:
            pass

        return None

    def _parse_timestamp(self, ts: str) -> Optional[datetime]:
        """Parse timestamp string to datetime."""
        try:
            parts = ts.split(':')
            if len(parts) == 2:
                return datetime(2000, 1, 1, 0, int(parts[0]), int(parts[1]))
            elif len(parts) == 3:
                return datetime(2000, 1, 1, int(parts[0]), int(parts[1]), int(parts[2]))
        except:
            pass
        return None

    # Gemini meta-instruction patterns to filter out
    GEMINI_META_PATTERNS = [
        r"review gemini's notes",
        r"get tips and learn",
        r"please provide feedback",
        r"short survey",
        r"you should review",
    ]

    def _extract_action_items(self, lines: List[TranscriptLine]) -> List[ActionItem]:
        """Extract action items from transcript lines."""
        action_items = []

        for line in lines:
            text = line.text

            # Skip Gemini meta-instructions
            text_lower = text.lower()
            if any(re.search(p, text_lower) for p in self.GEMINI_META_PATTERNS):
                continue

            for pattern, confidence, assignee_source in self.ACTION_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    action = match.group('action').strip()

                    # Clean up action text (remove trailing punctuation, etc.)
                    action = re.sub(r'[.!?,;]+$', '', action)
                    action = action.strip()

                    # Skip very short or generic actions
                    if len(action) < 5:
                        continue

                    # Determine assignee
                    assignee = None
                    if assignee_source == "person" and 'person' in match.groupdict():
                        assignee = match.group('person').strip().lstrip('@')
                    elif assignee_source == "speaker":
                        assignee = line.speaker

                    # Extract deadline if present
                    deadline = self._extract_deadline(text)

                    action_items.append(ActionItem(
                        description=action,
                        assignee=assignee,
                        source_line=text,
                        speaker=line.speaker,
                        confidence=confidence,
                        deadline=deadline,
                    ))

                    # Only match first pattern (highest confidence)
                    break

        return action_items

    def _extract_decisions(self, lines: List[TranscriptLine]) -> List[Decision]:
        """Extract decisions from transcript lines."""
        decisions = []

        for i, line in enumerate(lines):
            text = line.text

            for pattern, confidence in self.DECISION_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    decision = match.group('decision').strip()

                    # Clean up
                    decision = re.sub(r'[.!?,;]+$', '', decision)
                    decision = decision.strip()

                    # Skip very short decisions
                    if len(decision) < 5:
                        continue

                    # Get context from surrounding lines
                    context_lines = []
                    if i > 0:
                        context_lines.append(lines[i-1].text)
                    context = ' '.join(context_lines)

                    decisions.append(Decision(
                        description=decision,
                        context=context,
                        source_line=text,
                        speaker=line.speaker,
                        confidence=confidence,
                    ))

                    # Only match first pattern
                    break

        return decisions

    def _extract_questions(self, lines: List[TranscriptLine]) -> List[Question]:
        """Extract questions from transcript lines."""
        questions = []

        for line in lines:
            text = line.text

            for pattern in self.QUESTION_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    question = match.group('question').strip()

                    # Skip very short questions
                    if len(question) < 10:
                        continue

                    # Skip common false positives
                    if question.lower().startswith(('how are', 'what time', 'can you hear')):
                        continue

                    questions.append(Question(
                        text=question,
                        speaker=line.speaker,
                        source_line=text,
                    ))
                    break

        return questions

    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract deadline from action item text."""
        for pattern in self.DEADLINE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group('deadline').strip()
        return None


def main():
    """CLI for testing the parser."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcription_parser.py <file>")
        print("       python transcription_parser.py --sample")
        sys.exit(1)

    if sys.argv[1] == "--sample":
        # Sample Google Meet transcript for testing
        sample = """
[00:00:15] John Smith: Let's start with the API update.
[00:00:32] Jane Doe: I'll have the PR ready by Friday.
[00:01:15] John Smith: Great. We decided to go with PostgreSQL for the database.
[00:01:45] Jane Doe: What about the rate limiting question?
[00:02:10] John Smith: We should discuss that at the weekly. @tadej needs to review the options.
[00:02:35] Jane Doe: Action item: schedule the security review for next week.
[00:03:00] John Smith: Going forward we'll use JWT for auth.
        """.strip()

        parser = TranscriptionParser()
        result = parser.parse(sample)

        print(f"Format detected: {result.format_detected}")
        print(f"Duration: ~{result.duration_estimate} minutes")
        print(f"Speakers: {', '.join(result.speakers)}")
        print()

        print("=== ACTION ITEMS ===")
        for action in result.action_items:
            assignee = f"@{action.assignee}" if action.assignee else "(unassigned)"
            deadline = f" [due: {action.deadline}]" if action.deadline else ""
            print(f"  [{action.confidence:.0%}] {action.description}")
            print(f"       -> {assignee}{deadline}")
            print()

        print("=== DECISIONS ===")
        for decision in result.decisions:
            print(f"  [{decision.confidence:.0%}] {decision.description}")
            print(f"       by {decision.speaker}")
            print()

        print("=== QUESTIONS ===")
        for question in result.questions_raised:
            print(f"  - {question.text}")
            print(f"    asked by {question.speaker}")
            print()

    else:
        # Parse file
        filepath = sys.argv[1]
        with open(filepath, 'r') as f:
            content = f.read()

        parser = TranscriptionParser()
        result = parser.parse(content)

        print(f"Parsed {filepath}")
        print(f"Format: {result.format_detected}")
        print(f"Stats: {result.summary_stats}")


if __name__ == "__main__":
    main()
