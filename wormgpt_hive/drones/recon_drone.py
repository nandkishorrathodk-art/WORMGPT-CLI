from typing import Any, Dict
from .base_drone import BaseDrone
import subprocess

class ReconDrone(BaseDrone):
    """Reconnaissance Drone: Performs network reconnaissance tasks such as port scanning and subdomain enumeration."""

    def __init__(self):
        super().__init__("ReconDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "port_scan": {
                "description": "Scans for open ports on a target host.",
                "parameters": [
                    {"name": "target", "type": "str", "description": "The target host to scan (IP address or hostname)."},
                    {"name": "ports", "type": "str", "optional": True, "description": "The ports to scan (e.g., '22,80,443', '1-1000'). Defaults to well-known ports."},
                ]
            },
            "check_nmap": {
                "description": "Checks if nmap is installed and available on the system.",
                "parameters": []
            },
            "subdomain_enumeration": {
                "description": "Enumerates subdomains for a given domain using subfinder.",
                "parameters": [
                    {"name": "domain", "type": "str", "description": "The domain to enumerate subdomains for."}
                ]
            },
            "check_subfinder": {
                "description": "Checks if subfinder is installed and available on the system.",
                "parameters": []
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "port_scan":
            return self._port_scan(parameters)
        elif action == "check_nmap":
            return self._check_nmap(parameters)
        elif action == "subdomain_enumeration":
            return self._subdomain_enumeration(parameters)
        elif action == "check_subfinder":
            return self._check_subfinder(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _check_nmap(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = subprocess.run(["nmap", "-V"], capture_output=True, text=True, check=True)
            return self._success_response({"version": result.stdout.strip()}, "nmap is available.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return self._error_response("nmap not found", "Please install nmap on the system.")

    def _port_scan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        check = self._check_nmap({})
        if not check["success"]:
            return check

        error = self._validate_parameters(parameters, ["target"])
        if error:
            return self._error_response(error)

        target = parameters["target"]
        ports = parameters.get("ports")

        command = ["nmap", "-sT", "-Pn"]
        if ports:
            command.extend(["-p", ports])
        command.append(target)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return self._success_response({"scan_output": result.stdout.strip()}, f"Port scan completed for {target}.")
        except subprocess.CalledProcessError as e:
            return self._error_response(f"Port scan failed for {target}", e.stderr.strip())
        except FileNotFoundError:
            return self._error_response("nmap not found", "Please install nmap on the system.")

    def _check_subfinder(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = subprocess.run(["subfinder", "-version"], capture_output=True, text=True, check=True)
            return self._success_response({"version": result.stdout.strip()}, "subfinder is available.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._error_response("subfinder not found", "Please install subfinder on the system.")

    def _subdomain_enumeration(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        check = self._check_subfinder({})
        if not check["success"]:
            return check

        error = self._validate_parameters(parameters, ["domain"])
        if error:
            return self._error_response(error)

        domain = parameters["domain"]

        command = ["subfinder", "-d", domain, "-silent"]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            subdomains = result.stdout.strip().split("\n")
            return self._success_response({"subdomains": subdomains}, f"Found {len(subdomains)} subdomains for {domain}.")
        except subprocess.CalledProcessError as e:
            return self._error_response(f"Subdomain enumeration failed for {domain}", e.stderr.strip())
        except FileNotFoundError:
            return self._error_response("subfinder not found", "Please install subfinder on the system.")
