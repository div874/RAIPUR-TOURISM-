"""
Base Place Connector.
Defines standard interface for all destination, eatery, and experience connectors.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class BasePlaceConnector(ABC):
    """
    Abstract Base Class for place data connectors.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, source_id: str, timeout: int = 10, max_retries: int = 2):
        self.name = name
        self.source_id = source_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"PlaceConnector.{source_id}")
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def safe_get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, verify_ssl: bool = True) -> Optional[requests.Response]:
        """
        Executes HTTP GET with retries and exponential backoff.
        """
        req_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            req_headers.update(headers)

        for attempt in range(1, self.max_retries + 1):
            try:
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
                    return response
            except requests.exceptions.SSLError:
                if verify_ssl:
                    try:
                        return self.session.get(url, headers=req_headers, params=params, timeout=self.timeout, verify=False)
                    except Exception:
                        pass
                self.logger.warning(f"SSL issue for {url}")
                return None
            except requests.exceptions.RequestException as err:
                self.logger.warning(f"Attempt {attempt}/{self.max_retries} failed for {url}: {err}")
                time.sleep(attempt * 1.0)
            except Exception as err:
                self.logger.error(f"Unexpected error for {url}: {err}")
                return None

        return None

    @abstractmethod
    def fetch_places(self, city_id: str) -> List[Dict[str, Any]]:
        """
        Fetches places for the designated city. Must handle all its own exceptions.
        """
        pass

    def run(self, city_id: str) -> List[Dict[str, Any]]:
        """
        Connector execution wrapper. Catches exceptions to avoid crashing pipeline.
        """
        self.logger.info(f"Extracting places from {self.name} for city: {city_id}")
        start = time.time()
        try:
            records = self.fetch_places(city_id)
            elapsed = time.time() - start
            self.logger.info(f"Extracted {len(records)} records from {self.name} in {elapsed:.2f}s")
            return records
        except Exception as exc:
            elapsed = time.time() - start
            self.logger.error(f"Failed extraction from {self.name} after {elapsed:.2f}s: {exc}", exc_info=True)
            return []

