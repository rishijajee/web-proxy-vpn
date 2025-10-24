"""
Sample Automation Scripts for Google Docs Operations
Demonstrates automated login and file operations
"""

from google_integration import GoogleDriveManager
from crypto_manager import CryptoManager, ProxyConfig
from network_checker import NetworkChecker
from pathlib import Path


def check_network_and_configure_proxy():
    """Check network status and configure proxy if needed"""
    print("=" * 60)
    print("STEP 1: Network Detection")
    print("=" * 60)

    # Check network without proxy
    checker = NetworkChecker()
    status = checker.get_network_status()

    print(f"\nNetwork Status: {status['status']}")
    print(f"Message: {status['message']}")

    if status['status'] == 'BLOCKED':
        print("\n⚠️  Google services are blocked!")
        print("Please configure a proxy in the web UI or programmatically.")

        # Example: Configure proxy programmatically
        crypto = CryptoManager()
        proxy_mgr = ProxyConfig(crypto)

        # Uncomment and fill in your proxy details:
        # proxy_mgr.save_proxy(
        #     proxy_type='socks5',
        #     host='your-proxy-host.com',
        #     port=1080,
        #     username='your_username',  # Optional
        #     password='your_password'   # Optional
        # )
        # print("✓ Proxy configured!")

    elif status['status'] == 'OPEN':
        print("\n✓ Google services are accessible directly!")

    return status['status']


def authenticate_google():
    """Authenticate with Google and return manager instance"""
    print("\n" + "=" * 60)
    print("STEP 2: Google Authentication")
    print("=" * 60)

    manager = GoogleDriveManager()

    if manager.is_authenticated():
        print("✓ Already authenticated with Google!")
        return manager
    else:
        print("\n⚠️  Not authenticated!")
        print("Please authenticate via the web UI:")
        print("1. Run: python app_google.py")
        print("2. Visit: http://localhost:5000")
        print("3. Click 'Login with Google'")
        print("4. Complete OAuth flow")
        return None


def list_recent_files(manager, count=10):
    """List recent Google Drive files"""
    print("\n" + "=" * 60)
    print(f"STEP 3: Listing {count} Recent Files")
    print("=" * 60)

    if not manager.initialize_services():
        print("✗ Failed to initialize Google services")
        return

    files = manager.list_files(page_size=count)

    if not files:
        print("\nNo files found in your Google Drive.")
        return

    print(f"\nFound {len(files)} files:\n")

    for i, file in enumerate(files, 1):
        print(f"{i}. 📄 {file['name']}")
        print(f"   Type: {file['mimeType'].split('.')[-1]}")
        print(f"   Modified: {file['modifiedTime'][:10]}")
        if file.get('webViewLink'):
            print(f"   Link: {file['webViewLink']}")
        print()


def search_files(manager, query):
    """Search for files in Google Drive"""
    print("\n" + "=" * 60)
    print(f"STEP 4: Searching for '{query}'")
    print("=" * 60)

    if not manager.initialize_services():
        print("✗ Failed to initialize Google services")
        return

    files = manager.search_files(query)

    if not files:
        print(f"\nNo files found matching '{query}'")
        return

    print(f"\nFound {len(files)} matching files:\n")

    for i, file in enumerate(files, 1):
        print(f"{i}. 📄 {file['name']}")
        print(f"   ID: {file['id']}")
        print()


def upload_sample_file(manager):
    """Upload a sample text file to Google Drive"""
    print("\n" + "=" * 60)
    print("STEP 5: Uploading Sample File")
    print("=" * 60)

    if not manager.initialize_services():
        print("✗ Failed to initialize Google services")
        return

    # Create sample file
    sample_file = Path("sample_upload.txt")
    sample_file.write_text("This is a sample file uploaded via automation script.\n"
                          "Created by Google Docs Proxy VPN application.\n"
                          "Timestamp: " + str(Path(__file__).stat().st_mtime))

    print(f"\n✓ Created sample file: {sample_file}")

    # Upload file
    result = manager.upload_file(str(sample_file))

    # Clean up
    sample_file.unlink()

    if result:
        print(f"\n✓ File uploaded successfully!")
        print(f"   Name: {result['name']}")
        print(f"   ID: {result['id']}")
        print(f"   Link: {result.get('webViewLink', 'N/A')}")
        return result['id']
    else:
        print("\n✗ Upload failed")
        return None


def download_file_example(manager, file_id):
    """Download a file from Google Drive"""
    print("\n" + "=" * 60)
    print("STEP 6: Downloading File")
    print("=" * 60)

    if not manager.initialize_services():
        print("✗ Failed to initialize Google services")
        return

    output_path = Path("downloads") / f"{file_id}.pdf"
    output_path.parent.mkdir(exist_ok=True)

    print(f"\nDownloading to: {output_path}")

    success = manager.download_file(file_id, str(output_path), export_format='pdf')

    if success:
        print(f"\n✓ File downloaded successfully!")
        print(f"   Path: {output_path}")
        print(f"   Size: {output_path.stat().st_size} bytes")
    else:
        print("\n✗ Download failed")


def create_folder_example(manager):
    """Create a folder in Google Drive"""
    print("\n" + "=" * 60)
    print("STEP 7: Creating Folder")
    print("=" * 60)

    if not manager.initialize_services():
        print("✗ Failed to initialize Google services")
        return

    folder_name = "ProxyVPN Automation Test"
    folder_id = manager.create_folder(folder_name)

    if folder_id:
        print(f"\n✓ Folder created successfully!")
        print(f"   Name: {folder_name}")
        print(f"   ID: {folder_id}")
        return folder_id
    else:
        print("\n✗ Folder creation failed")
        return None


def main():
    """Run all automation examples"""
    print("\n" + "=" * 70)
    print("  GOOGLE DOCS PROXY VPN - AUTOMATION EXAMPLES")
    print("=" * 70)

    # Step 1: Check network
    network_status = check_network_and_configure_proxy()

    # Step 2: Authenticate
    manager = authenticate_google()

    if not manager:
        print("\n❌ Cannot proceed without authentication.")
        print("Please complete OAuth setup first.")
        return

    # Step 3: List recent files
    list_recent_files(manager, count=5)

    # Step 4: Search files
    search_files(manager, "test")

    # Step 5: Upload file
    uploaded_file_id = upload_sample_file(manager)

    # Step 6: Download file (if upload succeeded)
    if uploaded_file_id:
        download_file_example(manager, uploaded_file_id)

    # Step 7: Create folder
    create_folder_example(manager)

    print("\n" + "=" * 70)
    print("  AUTOMATION COMPLETE")
    print("=" * 70)
    print("\n✓ All operations completed!")
    print("Check your Google Drive to verify the changes.")


if __name__ == "__main__":
    main()
