"""
Base Event Source Connector.
Defines standard interface, bounded retries, rate-limiting, and resilient error reporting.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import urllib3

# Suppress insecure request warnings for institutions with local government SSL cert chains
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class BaseConnector(ABC):
    """
    Abstract Base Class for all event source connectors.
    Ensures safe, bounded execution without crashing the main pipeline.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, source_id: str, timeout: int = 10, max_retries: int = 2, delay_between_requests: float = 0.5):
        self.name = name
        self.source_id = source_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.logger = logging.getLogger(f"Connector.{source_id}")
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def safe_get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, verify_ssl: bool = True) -> Optional[requests.Response]:
        """
        Performs an HTTP GET with bounded retries and exponential backoff.
        Never throws unhandled exceptions outside this method.
        """
        req_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            req_headers.update(headers)

        for attempt in range(1, self.max_retries + 1):
            try:
                time.sleep(self.delay_between_requests)
                response = self.session.get(url, headers=req_headers, params=params, timeout=self.timeout, verify=verify_ssl)
                if response.status_code == 200:
                    return response
                elif response.status_code in [404, 410]:
                    self.logger.warning(f"Resource not found ({response.status_code}): {url}")
                    return None
                elif response.status_code in [429, 500, 502, 503, 504]:
                    self.logger.warning(f"Attempt {attempt}/{self.max_retries} received {response.status_code} from {url}")
                    time.sleep(attempt * 1.5)
                else:
                    self.logger.warning(f"Unexpected status code {response.status_code} from {url}")
                    return response
            except requests.exceptions.SSLError:
                # Retry once without SSL verification if host has local self-signed or state cert
                if verify_ssl:
                    try:
                        return self.session.get(url, headers=req_headers, params=params, timeout=self.timeout, verify=False)
                    except Exception:
                        pass
                self.logger.warning(f"SSL certificate issue for {url}")
                return None
            except requests.exceptions.Timeout:
                self.logger.warning(f"Attempt {attempt}/{self.max_retries} timed out connecting to {url}")
                time.sleep(attempt * 1.0)
            except requests.exceptions.RequestException as err:
                self.logger.warning(f"Attempt {attempt}/{self.max_retries} request failed for {url}: {err}")
                time.sleep(attempt * 1.0)
            except Exception as err:
                self.logger.error(f"Unexpected error fetching {url}: {err}")
                return None

        self.logger.error(f"Max retries exceeded for {url}")
        return None

    @abstractmethod
    def fetch_records(self) -> List[Dict[str, Any]]:
        """
        Fetches raw or semi-structured records from the source.
        Returns a list of raw event items. Must handle all its own exceptions.
        """
        pass

    def run(self) -> List[Dict[str, Any]]:
        """
        Executes the connector workflow and returns extracted candidate events.
        Guarantees that errors in this connector do not stop other connectors.
        """
        self.logger.info(f"Starting extraction for source: {self.name}")
        start_time = time.time()
        try:
            records = self.fetch_records()
            elapsed = time.time() - start_time
            self.logger.info(f"Completed {self.name}: extracted {len(records)} raw candidate records in {elapsed:.2f}s")
            return records
        except Exception as exc:
            elapsed = time.time() - start_time
            self.logger.error(f"Failed extraction for {self.name} after {elapsed:.2f}s: {exc}", exc_info=True)
            return []
