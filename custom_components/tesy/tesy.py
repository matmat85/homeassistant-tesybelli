"""Tesy integration."""

from __future__ import annotations

import logging
from typing import Any

from urllib.parse import urlparse, urlencode
import requests
import json

from .const import (
    ATTR_POWER,
    ATTR_TARGET_TEMP,
    ATTR_BOOST,
    ATTR_MODE,
    HTTP_TIMEOUT,
    IP_ADDRESS,
    HEATER_POWER,
)


_LOGGER = logging.getLogger(__name__)


class Tesy:
    """Tesy instance."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Init Tesy."""
        self._ip_address = data[IP_ADDRESS]

        self._heater_power = 2400
        if HEATER_POWER in data:
            self._heater_power = data[HEATER_POWER]

    def get_data(self) -> dict[str, Any]:
        """Get data for Tesy component."""
        return self._get_request(name="_all").json()

    def set_target_temperature(self, val: int) -> bool:
        """Set target temperature for Tesy component."""
        return self._get_request(name=ATTR_TARGET_TEMP, set=val).json()

    def set_power(self, val: str) -> bool:
        """Set power for Tesy component."""
        return self._get_request(name=ATTR_POWER, set=val).json()

    def set_boost(self, val: str) -> bool:
        """Set boost for Tesy component."""
        return self._get_request(name=ATTR_BOOST, set=val).json()

    def set_operation_mode(self, val: str) -> bool:
        """Set boost for Tesy component."""
        return self._get_request(name=ATTR_MODE, set=val).json()

    def probe_esp32_info(self) -> dict[str, Any]:
        """Probe ESP32 for additional information and capabilities."""
        esp32_info = {
            "endpoints_discovered": [],
            "system_info": {},
            "wifi_info": {},
            "firmware_info": {},
            "debug_info": {},
            "available_apis": []
        }
        
        # Common ESP32 endpoints to probe
        endpoints_to_test = [
            "/",
            "/info",
            "/status",
            "/system",
            "/wifi",
            "/debug",
            "/heap",
            "/firmware",
            "/version",
            "/config",
            "/scan",
            "/restart",
            "/reset",
            "/update",
            "/files",
            "/fs",
            "/spiffs",
            "/littlefs",
            "/api/info",
            "/api/status",
            "/api/system",
            "/api/wifi",
            "/api/debug",
            "/api/heap",
            "/api/version",
            "/api/config",
            "/json",
            "/data.json",
            "/status.json",
            "/info.json",
            "/manifest.json"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = self._probe_endpoint(endpoint)
                if response:
                    esp32_info["endpoints_discovered"].append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", "unknown"),
                        "content_length": len(response.text),
                        "response_preview": response.text[:200] if len(response.text) > 200 else response.text
                    })
                    
                    # Try to parse JSON responses for additional data
                    if "json" in response.headers.get("content-type", "").lower():
                        try:
                            json_data = response.json()
                            if endpoint in ["/info", "/api/info"]:
                                esp32_info["system_info"].update(json_data)
                            elif endpoint in ["/wifi", "/api/wifi"]:
                                esp32_info["wifi_info"].update(json_data)
                            elif endpoint in ["/debug", "/api/debug"]:
                                esp32_info["debug_info"].update(json_data)
                            elif endpoint in ["/version", "/api/version", "/firmware"]:
                                esp32_info["firmware_info"].update(json_data)
                        except json.JSONDecodeError:
                            pass
                        
            except Exception as e:
                _LOGGER.debug(f"Failed to probe endpoint {endpoint}: {e}")
        
        return esp32_info

    def get_esp32_system_info(self) -> dict[str, Any]:
        """Get ESP32 system information."""
        system_info = {}
        
        # Try different endpoints that might contain system info
        info_endpoints = ["/info", "/api/info", "/system", "/api/system", "/status", "/api/status"]
        
        for endpoint in info_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        system_info[f"from_{endpoint.replace('/', '_')}"] = data
                    except:
                        system_info[f"from_{endpoint.replace('/', '_')}_raw"] = response.text[:500]
            except:
                continue
                
        return system_info

    def get_esp32_wifi_info(self) -> dict[str, Any]:
        """Get detailed WiFi information from ESP32."""
        wifi_info = {}
        
        # Try WiFi-specific endpoints
        wifi_endpoints = ["/wifi", "/api/wifi", "/scan", "/api/scan"]
        
        for endpoint in wifi_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        wifi_info[f"from_{endpoint.replace('/', '_')}"] = data
                    except:
                        wifi_info[f"from_{endpoint.replace('/', '_')}_raw"] = response.text[:500]
            except:
                continue
                
        return wifi_info

    def get_esp32_filesystem_info(self) -> dict[str, Any]:
        """Get ESP32 filesystem information."""
        fs_info = {}
        
        # Try filesystem endpoints
        fs_endpoints = ["/files", "/fs", "/spiffs", "/littlefs", "/api/files"]
        
        for endpoint in fs_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        fs_info[f"from_{endpoint.replace('/', '_')}"] = data
                    except:
                        fs_info[f"from_{endpoint.replace('/', '_')}_raw"] = response.text[:500]
            except:
                continue
                
        return fs_info

    def get_specific_endpoint(self, endpoint: str) -> dict[str, Any]:
        """Get data from a specific endpoint."""
        try:
            response = self._probe_endpoint(endpoint)
            if response and response.status_code == 200:
                result = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_length": len(response.text),
                    "raw_content": response.text
                }
                
                # Try to parse as JSON
                content_type = response.headers.get("content-type", "").lower()
                if "json" in content_type:
                    try:
                        result["json_content"] = response.json()
                    except:
                        result["json_parse_error"] = "Failed to parse JSON"
                
                # Extract useful info from HTML
                elif "html" in content_type:
                    result["content_type"] = "HTML"
                    # Look for common patterns
                    if "esp32" in response.text.lower():
                        result["contains_esp32_info"] = True
                    if "version" in response.text.lower():
                        result["contains_version_info"] = True
                
                return result
            else:
                return {
                    "endpoint": endpoint,
                    "error": f"HTTP {response.status_code if response else 'No response'}"
                }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "error": str(e)
            }

    def test_custom_endpoints(self, endpoints: list[str]) -> dict[str, Any]:
        """Test a custom list of endpoints."""
        results = {}
        for endpoint in endpoints:
            results[endpoint] = self.get_specific_endpoint(endpoint)
        return results

    def scan_for_json_endpoints(self) -> dict[str, Any]:
        """Specifically scan for JSON-returning endpoints."""
        json_endpoints = [
            "/api",
            "/api/all",
            "/api/status", 
            "/api/info",
            "/api/config",
            "/api/wifi",
            "/api/system",
            "/api/debug",
            "/api/heap",
            "/api/version",
            "/status.json",
            "/info.json",
            "/config.json",
            "/system.json",
            "/data.json",
            "/manifest.json"
        ]
        
        json_results = {}
        for endpoint in json_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    content_type = response.headers.get("content-type", "").lower()
                    if "json" in content_type or endpoint.endswith(".json"):
                        try:
                            json_data = response.json()
                            json_results[endpoint] = {
                                "status": "success",
                                "data": json_data,
                                "keys": list(json_data.keys()) if isinstance(json_data, dict) else "not_dict"
                            }
                        except:
                            json_results[endpoint] = {
                                "status": "json_parse_failed",
                                "raw_content": response.text[:200]
                            }
            except:
                continue
                
        return json_results

    def get_esp32_chip_info(self) -> dict[str, Any]:
        """Get detailed ESP32 chip information."""
        chip_info = {}
        
        # Try ESP32-specific endpoints
        chip_endpoints = ["/chip", "/api/chip", "/system", "/api/system", "/info", "/api/info"]
        
        for endpoint in chip_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        # Look for chip-specific information
                        chip_fields = [
                            'chip_id', 'chip_model', 'chip_revision', 'chip_cores',
                            'flash_size', 'flash_speed', 'psram_size', 'cpu_freq',
                            'sdk_version', 'esp_idf_version', 'arduino_version'
                        ]
                        
                        for field in chip_fields:
                            if field in data:
                                chip_info[field] = data[field]
                                
                    except:
                        # If not JSON, look for text patterns
                        text = response.text.lower()
                        if 'esp32' in text:
                            chip_info[f"{endpoint}_contains_esp32"] = True
                        if 'chip' in text:
                            chip_info[f"{endpoint}_contains_chip_info"] = True
            except:
                continue
                
        return chip_info

    def get_esp32_performance_metrics(self) -> dict[str, Any]:
        """Get ESP32 performance and diagnostic metrics."""
        metrics = {}
        
        # Performance monitoring endpoints
        perf_endpoints = ["/metrics", "/api/metrics", "/heap", "/api/heap", "/stats", "/api/stats"]
        
        for endpoint in perf_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Look for performance metrics
                        perf_fields = [
                            'free_heap', 'total_heap', 'heap_size', 'heap_usage',
                            'cpu_load', 'cpu_usage', 'temperature', 'voltage',
                            'tasks_running', 'tasks_total', 'stack_high_water'
                        ]
                        
                        for field in perf_fields:
                            if field in data:
                                metrics[f"{endpoint}_{field}"] = data[field]
                                
                    except:
                        pass
            except:
                continue
                
        return metrics

    def get_esp32_network_details(self) -> dict[str, Any]:
        """Get detailed network configuration and statistics."""
        network_info = {}
        
        # Network-specific endpoints
        network_endpoints = [
            "/network", "/api/network", "/wifi", "/api/wifi",
            "/ethernet", "/api/ethernet", "/ip", "/api/ip"
        ]
        
        for endpoint in network_endpoints:
            try:
                response = self._probe_endpoint(endpoint)
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        network_info[f"from_{endpoint.replace('/', '_')}"] = data
                    except:
                        # Look for network info in text
                        text = response.text
                        if len(text) < 1000:  # Avoid huge responses
                            network_info[f"from_{endpoint.replace('/', '_')}_text"] = text[:200]
            except:
                continue
                
        return network_info

    def _probe_endpoint(self, endpoint: str, timeout: int = 5) -> requests.Response:
        """Probe a specific endpoint on the ESP32."""
        url = f"http://{self._ip_address}{endpoint}"
        
        try:
            response = requests.get(url, timeout=timeout)
            _LOGGER.debug(f"Probed {endpoint}: {response.status_code}")
            return response
        except Exception as e:
            _LOGGER.debug(f"Failed to probe {endpoint}: {e}")
            return None

    def _get_request(self, **kwargs) -> requests.Response:
        """Make GET request to the Tesy API."""
        url = urlparse(f"http://{self._ip_address}/api")
        url = url._replace(query=urlencode(kwargs))

        _LOGGER.debug(f"Tesy request: GET {url.geturl()}")
        try:
            r = requests.get(url.geturl(), timeout=HTTP_TIMEOUT)
            r.raise_for_status()
            _LOGGER.debug(f"Tesy status: {r.status_code}")
            _LOGGER.debug(f"Tesy response: {r.text}")

            return r
        except TimeoutError as timeout_error:
            raise ConnectionError from timeout_error
        except requests.exceptions.ConnectionError as connection_error:
            raise ConnectionError from connection_error
        except requests.exceptions.HTTPError as http_error:
            raise ConnectionError from http_error
