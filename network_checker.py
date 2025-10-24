"""
Network Detection Module
Checks connectivity to Google services and determines network restriction level
"""

import requests
import socket
from typing import Dict, Literal
from datetime import datetime

NetworkStatus = Literal["OPEN", "RESTRICTED", "BLOCKED"]

class NetworkChecker:
    """Detects network restrictions for Google services"""

    GOOGLE_SERVICES = {
        'docs': 'https://docs.google.com',
        'drive': 'https://drive.google.com',
        'accounts': 'https://accounts.google.com',
        'apis': 'https://www.googleapis.com'
    }

    TIMEOUT = 5  # seconds

    def __init__(self, proxy_config: Dict = None):
        """
        Initialize network checker

        Args:
            proxy_config: Optional proxy configuration dict with 'http' and 'https' keys
        """
        self.proxy_config = proxy_config
        self.last_check = None
        self.last_status = None

    def check_single_service(self, name: str, url: str) -> Dict:
        """
        Check connectivity to a single service

        Returns:
            Dict with 'accessible', 'status_code', 'error' keys
        """
        try:
            response = requests.get(
                url,
                timeout=self.TIMEOUT,
                proxies=self.proxy_config,
                allow_redirects=True,
                verify=False  # Disable SSL verification for restricted networks
            )
            return {
                'accessible': True,
                'status_code': response.status_code,
                'error': None
            }
        except requests.exceptions.Timeout:
            return {
                'accessible': False,
                'status_code': None,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'accessible': False,
                'status_code': None,
                'error': 'Connection refused or blocked'
            }
        except Exception as e:
            return {
                'accessible': False,
                'status_code': None,
                'error': str(e)
            }

    def check_all_services(self) -> Dict[str, Dict]:
        """
        Check connectivity to all Google services

        Returns:
            Dict mapping service names to their status
        """
        results = {}
        for name, url in self.GOOGLE_SERVICES.items():
            results[name] = self.check_single_service(name, url)

        self.last_check = datetime.now()
        return results

    def get_network_status(self) -> Dict:
        """
        Determine overall network status for Google services

        Returns:
            Dict with 'status', 'accessible_count', 'total_count', 'services', 'message'
        """
        service_results = self.check_all_services()

        accessible_count = sum(1 for result in service_results.values() if result['accessible'])
        total_count = len(service_results)

        # Determine status
        if accessible_count == total_count:
            status: NetworkStatus = "OPEN"
            message = "All Google services are accessible"
        elif accessible_count > 0:
            status: NetworkStatus = "RESTRICTED"
            message = f"Partial access: {accessible_count}/{total_count} services accessible"
        else:
            status: NetworkStatus = "BLOCKED"
            message = "All Google services are blocked"

        self.last_status = status

        return {
            'status': status,
            'accessible_count': accessible_count,
            'total_count': total_count,
            'services': service_results,
            'message': message,
            'timestamp': self.last_check.isoformat(),
            'proxy_enabled': self.proxy_config is not None
        }

    def requires_proxy(self) -> bool:
        """Check if proxy is required to access Google services"""
        if self.last_status is None:
            self.get_network_status()
        return self.last_status in ["RESTRICTED", "BLOCKED"]

    def test_dns_resolution(self, hostname: str = "docs.google.com") -> bool:
        """
        Test if DNS resolution works for Google domains

        Returns:
            True if DNS resolves successfully
        """
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False


def quick_check() -> NetworkStatus:
    """
    Quick network check without detailed results

    Returns:
        "OPEN", "RESTRICTED", or "BLOCKED"
    """
    checker = NetworkChecker()
    result = checker.get_network_status()
    return result['status']


if __name__ == "__main__":
    # Test the network checker
    print("Testing Network Connectivity to Google Services...")
    print("=" * 60)

    checker = NetworkChecker()
    status = checker.get_network_status()

    print(f"\nOverall Status: {status['status']}")
    print(f"Message: {status['message']}")
    print(f"Timestamp: {status['timestamp']}")
    print(f"\nDetailed Results:")
    print("-" * 60)

    for service, result in status['services'].items():
        icon = "✓" if result['accessible'] else "✗"
        print(f"{icon} {service:12} - {checker.GOOGLE_SERVICES[service]}")
        if not result['accessible']:
            print(f"  Error: {result['error']}")

    print("\n" + "=" * 60)
    print(f"Proxy Required: {checker.requires_proxy()}")
