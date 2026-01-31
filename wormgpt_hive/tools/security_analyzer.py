import json
import subprocess
import tempfile
import os
from typing import Any, Dict, List
from .base_tool import BaseTool


class SecurityAnalyzerTool(BaseTool):
    """Security Analyzer Tool: Analyzes Solidity smart contracts for vulnerabilities using Slither static analysis."""

    def __init__(self):
        super().__init__()
        self._verify_slither_installation()

    def _verify_slither_installation(self) -> bool:
        try:
            result = subprocess.run(
                ["slither", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        actions = {
            "analyze_contract": self.analyze_contract,
            "analyze_file": self.analyze_file,
            "get_vulnerability_report": self.get_vulnerability_report,
            "check_slither_available": self.check_slither_available,
        }

        if action not in actions:
            return self._error_response(f"Unknown action: {action}")

        try:
            return actions[action](**kwargs)
        except Exception as e:
            return self._error_response(str(e), f"Action: {action}")

    def check_slither_available(self) -> Dict[str, Any]:
        available = self._verify_slither_installation()
        return self._success_response(
            {"available": available},
            "Slither is available" if available else "Slither is not installed",
        )

    def analyze_contract(
        self, contract_code: str, contract_name: str = "Contract"
    ) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sol", delete=False
            ) as f:
                f.write(contract_code)
                temp_file = f.name

            try:
                result = self.analyze_file(
                    file_path=temp_file, contract_name=contract_name
                )
                return result
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            return self._error_response(f"Failed to analyze contract: {str(e)}")

    def analyze_file(self, file_path: str, contract_name: str = None) -> Dict[str, Any]:
        try:
            if not os.path.exists(file_path):
                return self._error_response(f"Contract file not found: {file_path}")

            cmd = ["slither", file_path, "--json", "-"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            vulnerabilities = []
            raw_output = result.stdout

            if result.returncode != 0 and not raw_output:
                return self._error_response("Slither analysis failed", result.stderr)

            try:
                if raw_output:
                    slither_output = json.loads(raw_output)
                    vulnerabilities = self._parse_slither_output(slither_output)
            except json.JSONDecodeError:
                pass

            severity_counts = self._count_severities(vulnerabilities)

            return self._success_response(
                {
                    "file_path": file_path,
                    "vulnerabilities": vulnerabilities,
                    "total_issues": len(vulnerabilities),
                    "severity_counts": severity_counts,
                    "raw_output": raw_output[:1000] if raw_output else "",
                },
                f"Analysis complete: {len(vulnerabilities)} issues found",
            )

        except subprocess.TimeoutExpired:
            return self._error_response("Slither analysis timed out")
        except Exception as e:
            return self._error_response(f"Analysis failed: {str(e)}")

    def get_vulnerability_report(
        self, vulnerabilities: List[Dict[str, Any]], format: str = "markdown"
    ) -> Dict[str, Any]:
        try:
            if format == "markdown":
                report = self._generate_markdown_report(vulnerabilities)
            elif format == "json":
                report = json.dumps(vulnerabilities, indent=2)
            elif format == "text":
                report = self._generate_text_report(vulnerabilities)
            else:
                return self._error_response(f"Unknown format: {format}")

            return self._success_response(
                {"report": report, "format": format}, f"Generated {format} report"
            )

        except Exception as e:
            return self._error_response(f"Failed to generate report: {str(e)}")

    def _parse_slither_output(
        self, slither_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if "results" in slither_output and "detectors" in slither_output["results"]:
            for detector in slither_output["results"]["detectors"]:
                vuln = {
                    "check": detector.get("check", "unknown"),
                    "impact": detector.get("impact", "Unknown"),
                    "confidence": detector.get("confidence", "Unknown"),
                    "description": detector.get("description", "No description"),
                    "elements": detector.get("elements", []),
                    "first_markdown_element": detector.get(
                        "first_markdown_element", ""
                    ),
                }
                vulnerabilities.append(vuln)

        vulnerabilities.sort(
            key=lambda x: (
                {
                    "High": 0,
                    "Medium": 1,
                    "Low": 2,
                    "Informational": 3,
                    "Optimization": 4,
                }.get(x["impact"], 5),
                {"High": 0, "Medium": 1, "Low": 2}.get(x["confidence"], 3),
            )
        )

        return vulnerabilities

    def _count_severities(
        self, vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        counts = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Informational": 0,
            "Optimization": 0,
        }

        for vuln in vulnerabilities:
            impact = vuln.get("impact", "Unknown")
            if impact in counts:
                counts[impact] += 1

        return counts

    def _generate_markdown_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        report = "# Smart Contract Security Analysis Report\n\n"

        severity_counts = self._count_severities(vulnerabilities)

        report += "## Summary\n\n"
        report += f"**Total Issues Found:** {len(vulnerabilities)}\n\n"
        report += "**Severity Breakdown:**\n"
        for severity, count in severity_counts.items():
            if count > 0:
                report += f"- **{severity}:** {count}\n"
        report += "\n---\n\n"

        report += "## Detailed Findings\n\n"

        for i, vuln in enumerate(vulnerabilities, 1):
            report += f"### {i}. {vuln['check']}\n\n"
            report += f"**Impact:** {vuln['impact']}  \n"
            report += f"**Confidence:** {vuln['confidence']}\n\n"
            report += f"**Description:**  \n{vuln['description']}\n\n"

            if vuln.get("elements"):
                report += "**Location:**\n"
                for elem in vuln["elements"][:3]:
                    if "source_mapping" in elem:
                        source = elem["source_mapping"]
                        if "filename_relative" in source:
                            report += (
                                f"- {source.get('filename_relative', 'unknown')}\n"
                            )

            report += "\n---\n\n"

        return report

    def _generate_text_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        report = "SMART CONTRACT SECURITY ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"

        severity_counts = self._count_severities(vulnerabilities)

        report += f"Total Issues: {len(vulnerabilities)}\n"
        for severity, count in severity_counts.items():
            if count > 0:
                report += f"{severity}: {count}\n"

        report += "\n" + "=" * 50 + "\n\n"

        for i, vuln in enumerate(vulnerabilities, 1):
            report += f"{i}. [{vuln['impact']}] {vuln['check']}\n"
            report += f"   {vuln['description']}\n\n"

        return report
