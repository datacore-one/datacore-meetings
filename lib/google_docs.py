"""
Google Docs Fetch Utility for Meetings Module.

Fetch-only utility for retrieving meeting transcripts from Google Docs.
NOT a full DIP-0010 sync adapter - just a simple fetch utility.

Usage:
    python google_docs.py setup      # First-time OAuth setup
    python google_docs.py test       # Test the connection
    python google_docs.py fetch URL  # Fetch document by URL
    python google_docs.py recent     # List recent Meet transcripts
"""

import os
import pickle
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse, parse_qs


@dataclass
class DocContent:
    """Represents fetched document content."""
    id: str
    title: str
    content: str
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    url: str


class GoogleDocsClient:
    """Fetch-only client for Google Docs API."""

    # Uses shared credentials from central .datacore/env/
    # Path: .datacore/modules/meetings/lib/google_docs.py
    # Target: .datacore/env/credentials/
    CREDS_DIR = Path(__file__).parent.parent.parent.parent / "env" / "credentials"
    TOKEN_FILE = CREDS_DIR / "google_docs_token.pickle"
    CLIENT_SECRETS_FILE = CREDS_DIR / "google_calendar_client_secret.json"

    # Scopes needed for read-only access
    SCOPES = [
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
    ]

    def __init__(self):
        self._docs_service = None
        self._drive_service = None

    def is_configured(self) -> bool:
        """Check if OAuth credentials are set up."""
        return self.TOKEN_FILE.exists() and self.CLIENT_SECRETS_FILE.exists()

    def get_credentials(self):
        """Get valid user credentials from storage or run auth flow."""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        creds = None

        # Load existing token
        if self.TOKEN_FILE.exists():
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, run auth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.CLIENT_SECRETS_FILE.exists():
                    print(f"ERROR: Client secrets file not found at {self.CLIENT_SECRETS_FILE}")
                    print("\nTo set up Google Docs access:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Select your existing project (or create one)")
                    print("3. Enable 'Google Docs API' and 'Google Drive API'")
                    print("4. The client secrets file should already exist from Calendar setup:")
                    print(f"   {self.CLIENT_SECRETS_FILE}")
                    print("\nIf you already have calendar access, just add the new scopes.")
                    sys.exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.CLIENT_SECRETS_FILE), self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for next run
            self.CREDS_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print(f"Credentials saved to {self.TOKEN_FILE}")

        return creds

    @property
    def docs_service(self):
        """Get or create Google Docs API service."""
        if self._docs_service is None:
            from googleapiclient.discovery import build
            creds = self.get_credentials()
            self._docs_service = build('docs', 'v1', credentials=creds)
        return self._docs_service

    @property
    def drive_service(self):
        """Get or create Google Drive API service."""
        if self._drive_service is None:
            from googleapiclient.discovery import build
            creds = self.get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def extract_doc_id_from_url(self, url: str) -> Optional[str]:
        """Extract document ID from Google Docs URL.

        Supports formats:
        - https://docs.google.com/document/d/{DOC_ID}/edit
        - https://docs.google.com/document/d/{DOC_ID}/edit?usp=sharing
        - https://docs.google.com/document/d/{DOC_ID}
        """
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_document_by_url(self, url: str) -> Optional[DocContent]:
        """Fetch document content by Google Docs URL."""
        doc_id = self.extract_doc_id_from_url(url)
        if not doc_id:
            print(f"ERROR: Could not extract document ID from URL: {url}")
            return None
        return self.get_document_by_id(doc_id)

    def get_document_by_id(self, doc_id: str) -> Optional[DocContent]:
        """Fetch document content by document ID."""
        try:
            # Get document from Docs API
            document = self.docs_service.documents().get(documentId=doc_id).execute()

            # Extract text content
            content = self._extract_text_content(document)

            # Try to get metadata from Drive API (optional)
            created_at = None
            modified_at = None
            try:
                file_metadata = self.drive_service.files().get(
                    fileId=doc_id,
                    fields='createdTime,modifiedTime'
                ).execute()

                if 'createdTime' in file_metadata:
                    created_at = datetime.fromisoformat(file_metadata['createdTime'].replace('Z', '+00:00'))
                if 'modifiedTime' in file_metadata:
                    modified_at = datetime.fromisoformat(file_metadata['modifiedTime'].replace('Z', '+00:00'))
            except Exception:
                # Drive API might not be enabled, continue without metadata
                pass

            return DocContent(
                id=doc_id,
                title=document.get('title', 'Untitled'),
                content=content,
                created_at=created_at,
                modified_at=modified_at,
                url=f"https://docs.google.com/document/d/{doc_id}/edit"
            )

        except Exception as e:
            print(f"ERROR: Failed to fetch document {doc_id}: {e}")
            return None

    def _extract_text_content(self, document: dict) -> str:
        """Extract plain text from Google Docs API response.

        The Docs API returns a complex structure with structural elements.
        This function extracts just the text content.
        """
        text_parts = []

        content = document.get('body', {}).get('content', [])

        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_parts.append(elem['textRun'].get('content', ''))

        return ''.join(text_parts)

    def find_meet_transcripts(self, days: int = 7) -> List[DocContent]:
        """Find Google Meet auto-transcripts and Gemini notes from Drive.

        Searches for files matching Meet transcript patterns:
        - Created in last N days
        - Title contains "Transcript" or "Notes by Gemini"
        """
        # Calculate time range
        time_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + 'Z'

        # Search for transcript documents (Transcript OR Gemini notes)
        query = f"mimeType='application/vnd.google-apps.document' and (name contains 'Transcript' or name contains 'Notes by Gemini') and createdTime > '{time_min}'"

        try:
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, createdTime, modifiedTime)",
                orderBy="createdTime desc",
                pageSize=20
            ).execute()

            files = results.get('files', [])
            transcripts = []

            for file in files:
                doc = self.get_document_by_id(file['id'])
                if doc:
                    transcripts.append(doc)

            return transcripts

        except Exception as e:
            print(f"ERROR: Failed to search for transcripts: {e}")
            return []

    def test_connection(self) -> bool:
        """Test the Google Docs/Drive connection."""
        try:
            creds = self.get_credentials()

            from googleapiclient.discovery import build

            # Test Docs API
            docs = build('docs', 'v1', credentials=creds)
            # Just verify we can build the service

            # Test Drive API
            drive = build('drive', 'v3', credentials=creds)
            about = drive.about().get(fields="user").execute()

            print("Successfully connected to Google Docs/Drive!")
            print(f"  Authenticated as: {about.get('user', {}).get('emailAddress', 'unknown')}")
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Google Docs Fetch Utility")
    parser.add_argument("command", choices=["setup", "test", "fetch", "recent"],
                       help="Command to run")
    parser.add_argument("url", nargs="?", help="Document URL (for fetch command)")
    parser.add_argument("--days", type=int, default=7,
                       help="Number of days to search (for recent command)")

    args = parser.parse_args()

    client = GoogleDocsClient()

    if args.command == "setup":
        print("Setting up Google Docs authentication...")
        print("(This will open a browser for OAuth consent)")
        client.get_credentials()
        print("\nAuthentication complete!")

    elif args.command == "test":
        client.test_connection()

    elif args.command == "fetch":
        if not args.url:
            print("ERROR: URL required for fetch command")
            print("Usage: python google_docs.py fetch <URL>")
            sys.exit(1)

        doc = client.get_document_by_url(args.url)
        if doc:
            print(f"\n=== {doc.title} ===\n")
            print(doc.content)
            print(f"\n---\nFetched from: {doc.url}")
            if doc.modified_at:
                print(f"Last modified: {doc.modified_at}")

    elif args.command == "recent":
        print(f"Searching for transcripts from the last {args.days} days...")
        transcripts = client.find_meet_transcripts(args.days)

        if not transcripts:
            print("No transcripts found.")
        else:
            print(f"\nFound {len(transcripts)} transcript(s):\n")
            for i, doc in enumerate(transcripts, 1):
                print(f"{i}. {doc.title}")
                print(f"   URL: {doc.url}")
                if doc.modified_at:
                    print(f"   Modified: {doc.modified_at.strftime('%Y-%m-%d %H:%M')}")
                print()


if __name__ == "__main__":
    main()
