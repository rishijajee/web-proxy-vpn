"""
Google Integration Module
Handles OAuth authentication and Google Drive/Docs API operations
"""

import os
import json
from typing import List, Dict, Optional, BinaryIO
from pathlib import Path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from crypto_manager import CryptoManager, GoogleTokenManager


class GoogleDriveManager:
    """Manages Google Drive and Docs operations"""

    # OAuth 2.0 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents'
    ]

    # Google Docs MIME types
    MIME_TYPES = {
        'document': 'application/vnd.google-apps.document',
        'spreadsheet': 'application/vnd.google-apps.spreadsheet',
        'presentation': 'application/vnd.google-apps.presentation',
        'folder': 'application/vnd.google-apps.folder',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain',
        'html': 'text/html',
        'csv': 'text/csv'
    }

    # Export formats for Google Docs
    EXPORT_FORMATS = {
        'document': {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'html': 'text/html'
        },
        'spreadsheet': {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv'
        },
        'presentation': {
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'pdf': 'application/pdf',
            'txt': 'text/plain'
        }
    }

    def __init__(self, client_secrets_file: str = "client_secrets.json",
                 crypto_manager: CryptoManager = None):
        """
        Initialize Google Drive Manager

        Args:
            client_secrets_file: Path to OAuth client secrets JSON file
            crypto_manager: CryptoManager instance for secure token storage
        """
        self.client_secrets_file = client_secrets_file
        self.crypto = crypto_manager or CryptoManager()
        self.token_manager = GoogleTokenManager(self.crypto)
        self.creds = None
        self.service = None
        self.docs_service = None

    def get_authorization_url(self, redirect_uri: str = "http://localhost:5000/oauth2callback") -> str:
        """
        Get OAuth authorization URL for user consent

        Args:
            redirect_uri: OAuth redirect URI

        Returns:
            Authorization URL string
        """
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Store state for verification
        self.crypto.update_credential('oauth_state', state)

        return authorization_url

    def handle_oauth_callback(self, authorization_response: str,
                               redirect_uri: str = "http://localhost:5000/oauth2callback") -> bool:
        """
        Handle OAuth callback and exchange code for tokens

        Args:
            authorization_response: Full callback URL with code
            redirect_uri: OAuth redirect URI

        Returns:
            True if successful
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            # Verify state
            stored_state = self.crypto.get_credential('oauth_state')
            flow.fetch_token(authorization_response=authorization_response)

            creds = flow.credentials

            # Save tokens
            self.token_manager.save_tokens(
                access_token=creds.token,
                refresh_token=creds.refresh_token,
                expiry=creds.expiry.isoformat() if creds.expiry else None
            )

            self.creds = creds
            return True

        except Exception as e:
            print(f"OAuth callback error: {e}")
            return False

    def load_credentials(self) -> bool:
        """
        Load credentials from storage and refresh if needed

        Returns:
            True if credentials are valid
        """
        token_data = self.token_manager.get_tokens()

        if not token_data:
            return False

        try:
            self.creds = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self._get_client_id(),
                client_secret=self._get_client_secret(),
                scopes=self.SCOPES
            )

            # Refresh if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                # Save refreshed tokens
                self.token_manager.save_tokens(
                    access_token=self.creds.token,
                    refresh_token=self.creds.refresh_token,
                    expiry=self.creds.expiry.isoformat() if self.creds.expiry else None
                )

            return True

        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False

    def _get_client_id(self) -> str:
        """Get client ID from secrets file"""
        with open(self.client_secrets_file, 'r') as f:
            data = json.load(f)
            return data['web']['client_id']

    def _get_client_secret(self) -> str:
        """Get client secret from secrets file"""
        with open(self.client_secrets_file, 'r') as f:
            data = json.load(f)
            return data['web']['client_secret']

    def initialize_services(self) -> bool:
        """
        Initialize Google Drive and Docs API services

        Returns:
            True if successful
        """
        if not self.creds:
            if not self.load_credentials():
                return False

        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error initializing services: {e}")
            return False

    def list_files(self, page_size: int = 20, query: str = None) -> List[Dict]:
        """
        List files in Google Drive

        Args:
            page_size: Number of files to return
            query: Optional query string (e.g., "mimeType='application/vnd.google-apps.document'")

        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            self.initialize_services()

        try:
            results = self.service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, webViewLink)",
                q=query
            ).execute()

            return results.get('files', [])

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def upload_file(self, file_path: str, folder_id: str = None,
                    convert_to_docs: bool = False) -> Optional[Dict]:
        """
        Upload a file to Google Drive

        Args:
            file_path: Local file path
            folder_id: Optional parent folder ID
            convert_to_docs: Convert to Google Docs format if applicable

        Returns:
            File metadata dict or None
        """
        if not self.service:
            self.initialize_services()

        try:
            file_name = Path(file_path).name
            file_metadata = {'name': file_name}

            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Detect MIME type
            mime_type = None
            if convert_to_docs:
                extension = Path(file_path).suffix.lower()
                if extension == '.docx':
                    mime_type = self.MIME_TYPES['document']
                elif extension == '.xlsx':
                    mime_type = self.MIME_TYPES['spreadsheet']
                elif extension == '.pptx':
                    mime_type = self.MIME_TYPES['presentation']

            media = MediaFileUpload(file_path, resumable=True)

            if mime_type:
                file_metadata['mimeType'] = mime_type

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink'
            ).execute()

            return file

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def download_file(self, file_id: str, output_path: str,
                      export_format: str = None) -> bool:
        """
        Download a file from Google Drive

        Args:
            file_id: Google Drive file ID
            output_path: Local path to save file
            export_format: Export format for Google Docs (e.g., 'docx', 'pdf')

        Returns:
            True if successful
        """
        if not self.service:
            self.initialize_services()

        try:
            # Get file metadata
            file = self.service.files().get(fileId=file_id, fields='mimeType, name').execute()
            mime_type = file['mimeType']

            # Check if it's a Google Doc that needs export
            if mime_type.startswith('application/vnd.google-apps'):
                if not export_format:
                    export_format = 'pdf'  # Default export format

                # Determine document type
                doc_type = None
                if 'document' in mime_type:
                    doc_type = 'document'
                elif 'spreadsheet' in mime_type:
                    doc_type = 'spreadsheet'
                elif 'presentation' in mime_type:
                    doc_type = 'presentation'

                if doc_type and export_format in self.EXPORT_FORMATS[doc_type]:
                    export_mime_type = self.EXPORT_FORMATS[doc_type][export_format]

                    request = self.service.files().export_media(
                        fileId=file_id,
                        mimeType=export_mime_type
                    )
                else:
                    print(f"Unsupported export format: {export_format} for {doc_type}")
                    return False
            else:
                # Regular file download
                request = self.service.files().get_media(fileId=file_id)

            # Download file
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")

            return True

        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

    def create_folder(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """
        Create a folder in Google Drive

        Args:
            folder_name: Name of the folder
            parent_id: Optional parent folder ID

        Returns:
            Folder ID or None
        """
        if not self.service:
            self.initialize_services()

        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': self.MIME_TYPES['folder']
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive

        Args:
            file_id: File ID to delete

        Returns:
            True if successful
        """
        if not self.service:
            self.initialize_services()

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

    def search_files(self, query: str) -> List[Dict]:
        """
        Search files in Google Drive

        Args:
            query: Search query (file name or content)

        Returns:
            List of matching files
        """
        search_query = f"name contains '{query}' or fullText contains '{query}'"
        return self.list_files(query=search_query)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.load_credentials()


if __name__ == "__main__":
    print("Google Drive Manager Module")
    print("=" * 60)
    print("\nThis module requires:")
    print("1. client_secrets.json file (OAuth credentials)")
    print("2. User authentication via OAuth flow")
    print("\nUse the Flask app to complete OAuth authentication.")
