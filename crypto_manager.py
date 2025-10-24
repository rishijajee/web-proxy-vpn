"""
Credential Management Module
Handles encryption/decryption of sensitive data like OAuth tokens and proxy credentials
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet
import base64
import hashlib

class CryptoManager:
    """Manages encryption and secure storage of credentials"""

    def __init__(self, config_dir: str = ".config"):
        """
        Initialize crypto manager

        Args:
            config_dir: Directory to store encrypted credentials (relative to project root)
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.key_file = self.config_dir / "secret.key"
        self.creds_file = self.config_dir / "credentials.enc"

        self.cipher = self._load_or_create_key()

    def _load_or_create_key(self) -> Fernet:
        """Load existing encryption key or create a new one"""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions on key file
            os.chmod(self.key_file, 0o600)

        return Fernet(key)

    def encrypt_data(self, data: Dict) -> bytes:
        """
        Encrypt dictionary data

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted bytes
        """
        json_data = json.dumps(data)
        return self.cipher.encrypt(json_data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> Dict:
        """
        Decrypt data back to dictionary

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted dictionary
        """
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

    def save_credentials(self, credentials: Dict) -> None:
        """
        Save credentials to encrypted file

        Args:
            credentials: Dictionary of credentials to save
        """
        encrypted = self.encrypt_data(credentials)
        with open(self.creds_file, "wb") as f:
            f.write(encrypted)
        # Set restrictive permissions
        os.chmod(self.creds_file, 0o600)

    def load_credentials(self) -> Optional[Dict]:
        """
        Load credentials from encrypted file

        Returns:
            Dictionary of credentials or None if file doesn't exist
        """
        if not self.creds_file.exists():
            return None

        try:
            with open(self.creds_file, "rb") as f:
                encrypted = f.read()
            return self.decrypt_data(encrypted)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None

    def update_credential(self, key: str, value: any) -> None:
        """
        Update a single credential value

        Args:
            key: Credential key
            value: Credential value
        """
        creds = self.load_credentials() or {}
        creds[key] = value
        self.save_credentials(creds)

    def get_credential(self, key: str, default=None) -> any:
        """
        Get a single credential value

        Args:
            key: Credential key
            default: Default value if key not found

        Returns:
            Credential value or default
        """
        creds = self.load_credentials() or {}
        return creds.get(key, default)

    def delete_credential(self, key: str) -> None:
        """
        Delete a credential

        Args:
            key: Credential key to delete
        """
        creds = self.load_credentials() or {}
        if key in creds:
            del creds[key]
            self.save_credentials(creds)

    def clear_all_credentials(self) -> None:
        """Delete all stored credentials"""
        if self.creds_file.exists():
            self.creds_file.unlink()

    def hash_password(self, password: str) -> str:
        """
        Create a secure hash of a password (for verification, not storage)

        Args:
            password: Password to hash

        Returns:
            Base64 encoded hash
        """
        hash_obj = hashlib.sha256(password.encode())
        return base64.b64encode(hash_obj.digest()).decode()


class ProxyConfig:
    """Helper class for managing proxy configurations"""

    def __init__(self, crypto_manager: CryptoManager):
        self.crypto = crypto_manager

    def save_proxy(self, proxy_type: str, host: str, port: int,
                   username: str = None, password: str = None) -> None:
        """
        Save proxy configuration

        Args:
            proxy_type: 'socks5', 'http', or 'https'
            host: Proxy hostname
            port: Proxy port
            username: Optional proxy username
            password: Optional proxy password
        """
        proxy_config = {
            'type': proxy_type,
            'host': host,
            'port': port,
            'username': username,
            'password': password
        }
        self.crypto.update_credential('proxy', proxy_config)

    def get_proxy(self) -> Optional[Dict]:
        """Get proxy configuration"""
        return self.crypto.get_credential('proxy')

    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration in requests/selenium format

        Returns:
            Dict with 'http' and 'https' keys, or None
        """
        config = self.get_proxy()
        if not config:
            return None

        proxy_type = config['type']
        host = config['host']
        port = config['port']
        username = config.get('username')
        password = config.get('password')

        # Build proxy URL
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"

        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def delete_proxy(self) -> None:
        """Delete proxy configuration"""
        self.crypto.delete_credential('proxy')


class GoogleTokenManager:
    """Helper class for managing Google OAuth tokens"""

    def __init__(self, crypto_manager: CryptoManager):
        self.crypto = crypto_manager

    def save_tokens(self, access_token: str, refresh_token: str = None,
                    expiry: str = None) -> None:
        """
        Save Google OAuth tokens

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expiry: Token expiry timestamp
        """
        token_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expiry': expiry
        }
        self.crypto.update_credential('google_tokens', token_data)

    def get_tokens(self) -> Optional[Dict]:
        """Get Google OAuth tokens"""
        return self.crypto.get_credential('google_tokens')

    def delete_tokens(self) -> None:
        """Delete Google OAuth tokens"""
        self.crypto.delete_credential('google_tokens')


if __name__ == "__main__":
    # Test the crypto manager
    print("Testing Credential Manager...")
    print("=" * 60)

    # Initialize manager
    crypto = CryptoManager(".test_config")
    proxy_mgr = ProxyConfig(crypto)
    token_mgr = GoogleTokenManager(crypto)

    # Test proxy storage
    print("\n1. Saving proxy configuration...")
    proxy_mgr.save_proxy('socks5', 'proxy.example.com', 1080, 'user123', 'pass456')
    print("   Saved!")

    print("\n2. Loading proxy configuration...")
    proxy = proxy_mgr.get_proxy()
    print(f"   {proxy}")

    print("\n3. Getting proxy dict for requests library...")
    proxy_dict = proxy_mgr.get_proxy_dict()
    print(f"   {proxy_dict}")

    # Test token storage
    print("\n4. Saving Google tokens...")
    token_mgr.save_tokens('access_token_12345', 'refresh_token_67890')
    print("   Saved!")

    print("\n5. Loading Google tokens...")
    tokens = token_mgr.get_tokens()
    print(f"   {tokens}")

    # Test general credential storage
    print("\n6. Saving custom credential...")
    crypto.update_credential('api_key', 'super_secret_key_123')
    print("   Saved!")

    print("\n7. Loading custom credential...")
    api_key = crypto.get_credential('api_key')
    print(f"   {api_key}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")

    # Cleanup
    import shutil
    shutil.rmtree(".test_config")
    print("Test config directory cleaned up.")
