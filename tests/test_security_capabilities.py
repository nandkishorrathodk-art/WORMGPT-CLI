import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch
from wormgpt_hive.tools.security_analyzer import SecurityAnalyzerTool
from wormgpt_hive.drones.security_drone import SecurityDrone
from wormgpt_hive.tools.file_system import FileSystemTool


class TestSecurityAnalyzerTool:

    @pytest.fixture
    def security_tool(self):
        with patch.object(
            SecurityAnalyzerTool, "_verify_slither_installation", return_value=True
        ):
            return SecurityAnalyzerTool()

    @pytest.fixture
    def sample_contract_path(self):
        base_path = Path(__file__).parent.parent
        return str(base_path / "samples" / "vulnerable_contract.sol")

    def test_tool_initialization(self, security_tool):
        assert security_tool is not None
        assert security_tool.name == "SecurityAnalyzerTool"

    def test_check_slither_available(self, security_tool):
        result = security_tool.check_slither_available()
        assert "available" in result["data"]

    @patch("subprocess.run")
    def test_analyze_file_success(self, mock_run, security_tool, sample_contract_path):
        mock_slither_output = {
            "results": {
                "detectors": [
                    {
                        "check": "reentrancy-eth",
                        "impact": "High",
                        "confidence": "High",
                        "description": "Reentrancy vulnerability detected",
                        "elements": [],
                    },
                    {
                        "check": "arbitrary-send-eth",
                        "impact": "Medium",
                        "confidence": "Medium",
                        "description": "Arbitrary ETH send detected",
                        "elements": [],
                    },
                ]
            }
        }

        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"results": {"detectors": [{"check": "reentrancy-eth", "impact": "High", "confidence": "High", "description": "Reentrancy vulnerability detected", "elements": []}]}}',
            stderr="",
        )

        result = security_tool.execute("analyze_file", file_path=sample_contract_path)

        assert result["success"] is True
        assert "vulnerabilities" in result["data"]
        assert "total_issues" in result["data"]
        assert "severity_counts" in result["data"]

    @patch("subprocess.run")
    def test_analyze_contract_code(self, mock_run, security_tool):
        contract_code = """
        pragma solidity ^0.8.0;
        contract Test {
            function test() public {}
        }
        """

        mock_run.return_value = Mock(
            returncode=0, stdout='{"results": {"detectors": []}}', stderr=""
        )

        result = security_tool.execute(
            "analyze_contract", contract_code=contract_code, contract_name="Test"
        )

        assert result["success"] is True

    def test_generate_markdown_report(self, security_tool):
        vulnerabilities = [
            {
                "check": "reentrancy-eth",
                "impact": "High",
                "confidence": "High",
                "description": "Reentrancy in withdraw function",
                "elements": [],
            }
        ]

        result = security_tool.execute(
            "get_vulnerability_report",
            vulnerabilities=vulnerabilities,
            format="markdown",
        )

        assert result["success"] is True
        assert "report" in result["data"]
        assert "Reentrancy" in result["data"]["report"]
        assert "High" in result["data"]["report"]

    def test_generate_text_report(self, security_tool):
        vulnerabilities = [
            {
                "check": "tx-origin",
                "impact": "Medium",
                "confidence": "Medium",
                "description": "Dangerous use of tx.origin",
                "elements": [],
            }
        ]

        result = security_tool.execute(
            "get_vulnerability_report", vulnerabilities=vulnerabilities, format="text"
        )

        assert result["success"] is True
        assert "report" in result["data"]
        assert "tx-origin" in result["data"]["report"]

    def test_unknown_action(self, security_tool):
        result = security_tool.execute("unknown_action")
        assert result["success"] is False
        assert "Unknown action" in result["error"]


class TestSecurityDrone:

    @pytest.fixture
    def security_drone(self):
        drone = SecurityDrone()

        with patch.object(
            SecurityAnalyzerTool, "_verify_slither_installation", return_value=True
        ):
            security_tool = SecurityAnalyzerTool()
        fs_tool = FileSystemTool()

        drone.register_tool("security_analyzer", security_tool)
        drone.register_tool("file_system", fs_tool)

        return drone

    @pytest.fixture
    def sample_contract_path(self):
        base_path = Path(__file__).parent.parent
        return str(base_path / "samples" / "vulnerable_contract.sol")

    @pytest.fixture
    def mock_vulnerability(self):
        return {
            "check": "reentrancy-eth",
            "impact": "High",
            "confidence": "High",
            "description": "Reentrancy vulnerability in withdraw function",
        }

    def test_drone_initialization(self, security_drone):
        assert security_drone is not None
        assert security_drone.name == "SecurityDrone"
        assert "security" in security_drone.description.lower()

    @patch("subprocess.run")
    def test_analyze_contract_file(
        self, mock_run, security_drone, sample_contract_path
    ):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"results": {"detectors": [{"check": "reentrancy-eth", "impact": "High", "confidence": "High", "description": "Test", "elements": []}]}}',
            stderr="",
        )

        result = security_drone.execute(
            "analyze_contract_file", {"file_path": sample_contract_path}
        )

        assert result["success"] is True
        assert result["drone"] == "SecurityDrone"

    def test_generate_poc_plan(self, security_drone, mock_vulnerability):
        result = security_drone.execute(
            "generate_poc_plan", {"vulnerability": mock_vulnerability}
        )

        assert result["success"] is True
        assert "exploitation_steps" in result["data"]
        assert "prerequisites" in result["data"]
        assert "expected_outcome" in result["data"]
        assert len(result["data"]["exploitation_steps"]) > 0

    def test_write_poc_exploit(self, security_drone, mock_vulnerability, tmp_path):
        output_file = str(tmp_path / "exploit.sol")

        result = security_drone.execute(
            "write_poc_exploit",
            {
                "vulnerability": mock_vulnerability,
                "output_file": output_file,
                "target_contract": "VulnerableBank",
            },
        )

        assert result["success"] is True
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()
            assert "ReentrancyAttack" in content
            assert "pragma solidity" in content

    def test_generate_security_report(self, security_drone, mock_vulnerability):
        vulnerabilities = [mock_vulnerability]

        result = security_drone.execute(
            "generate_security_report",
            {"vulnerabilities": vulnerabilities, "format": "markdown"},
        )

        assert result["success"] is True
        assert "report" in result["data"]

    @patch("subprocess.run")
    def test_full_security_audit(
        self, mock_run, security_drone, sample_contract_path, tmp_path
    ):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"results": {"detectors": [{"check": "reentrancy-eth", "impact": "High", "confidence": "High", "description": "Test vuln", "elements": []}]}}',
            stderr="",
        )

        report_output = str(tmp_path / "audit_report.md")
        poc_output = str(tmp_path / "exploit.sol")

        result = security_drone.execute(
            "full_security_audit",
            {
                "file_path": sample_contract_path,
                "generate_report": True,
                "report_output": report_output,
                "generate_poc": True,
                "poc_output": poc_output,
            },
        )

        assert result["success"] is True
        assert "analysis" in result["data"]

    def test_missing_parameters(self, security_drone):
        result = security_drone.execute("analyze_contract_file", {})
        assert result["success"] is False
        assert "Missing required parameters" in result["error"]

    def test_unknown_action(self, security_drone):
        result = security_drone.execute("unknown_action", {})
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    def test_poc_generation_for_different_vulnerabilities(
        self, security_drone, tmp_path
    ):
        vulnerabilities = [
            {"check": "reentrancy-eth", "impact": "High"},
            {"check": "arbitrary-send-eth", "impact": "Medium"},
            {"check": "unprotected-upgrade", "impact": "High"},
            {"check": "unknown-vuln", "impact": "Low"},
        ]

        for i, vuln in enumerate(vulnerabilities):
            output_file = str(tmp_path / f"exploit_{i}.sol")

            result = security_drone.execute(
                "write_poc_exploit", {"vulnerability": vuln, "output_file": output_file}
            )

            assert result["success"] is True
            assert os.path.exists(output_file)


class TestSecurityIntegration:

    @pytest.fixture
    def integrated_setup(self):
        drone = SecurityDrone()

        with patch.object(
            SecurityAnalyzerTool, "_verify_slither_installation", return_value=True
        ):
            security_tool = SecurityAnalyzerTool()
        fs_tool = FileSystemTool()

        drone.register_tool("security_analyzer", security_tool)
        drone.register_tool("file_system", fs_tool)

        base_path = Path(__file__).parent.parent
        sample_contract = str(base_path / "samples" / "vulnerable_contract.sol")

        return {
            "drone": drone,
            "security_tool": security_tool,
            "fs_tool": fs_tool,
            "sample_contract": sample_contract,
        }

    @patch("subprocess.run")
    def test_end_to_end_security_workflow(self, mock_run, integrated_setup, tmp_path):
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"results": {"detectors": [{"check": "reentrancy-eth", "impact": "High", "confidence": "High", "description": "Reentrancy detected", "elements": []}]}}',
            stderr="",
        )

        drone = integrated_setup["drone"]
        sample_contract = integrated_setup["sample_contract"]

        analysis_result = drone.execute(
            "analyze_contract_file", {"file_path": sample_contract}
        )

        assert analysis_result["success"] is True

        vulnerabilities = analysis_result["data"]["vulnerabilities"]

        if vulnerabilities:
            report_result = drone.execute(
                "generate_security_report",
                {"vulnerabilities": vulnerabilities, "format": "markdown"},
            )
            assert report_result["success"] is True

            high_severity = [v for v in vulnerabilities if v["impact"] == "High"]
            if high_severity:
                poc_file = str(tmp_path / "exploit.sol")
                poc_result = drone.execute(
                    "write_poc_exploit",
                    {"vulnerability": high_severity[0], "output_file": poc_file},
                )
                assert poc_result["success"] is True
