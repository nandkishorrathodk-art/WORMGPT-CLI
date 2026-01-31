import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wormgpt_hive.tools.security_analyzer import SecurityAnalyzerTool
from wormgpt_hive.drones.security_drone import SecurityDrone
from wormgpt_hive.tools.file_system import FileSystemTool


def demo_security_analyzer():
    print("=" * 60)
    print("WormGPT Security Analysis Demo")
    print("=" * 60)
    print()
    
    security_tool = SecurityAnalyzerTool()
    
    print("1. Checking Slither availability...")
    slither_check = security_tool.check_slither_available()
    print(f"   Slither available: {slither_check['data']['available']}")
    print()
    
    if not slither_check['data']['available']:
        print("   [!] Slither not installed. Install with: pip install slither-analyzer")
        print("   Continuing with mock analysis for demonstration...")
        print()
    
    base_path = Path(__file__).parent.parent
    sample_contract = str(base_path / "samples" / "vulnerable_contract.sol")
    
    if not os.path.exists(sample_contract):
        print(f"   [!] Sample contract not found at {sample_contract}")
        return
    
    print(f"2. Analyzing contract: {sample_contract}")
    print()
    
    analysis_result = security_tool.execute("analyze_file", file_path=sample_contract)
    
    if analysis_result["success"]:
        data = analysis_result["data"]
        print(f"   [+] Analysis complete!")
        print(f"   Total issues found: {data['total_issues']}")
        print()
        
        print("   Severity breakdown:")
        for severity, count in data["severity_counts"].items():
            if count > 0:
                print(f"   - {severity}: {count}")
        print()
        
        if data["vulnerabilities"]:
            print("3. Top vulnerabilities:")
            for i, vuln in enumerate(data["vulnerabilities"][:3], 1):
                print(f"\n   [{i}] {vuln['check']}")
                print(f"       Impact: {vuln['impact']}")
                print(f"       Confidence: {vuln['confidence']}")
                print(f"       Description: {vuln['description'][:100]}...")
        
        print("\n" + "=" * 60)
        print("Security Drone Demo")
        print("=" * 60)
        print()
        
        drone = SecurityDrone()
        drone.register_tool("security_analyzer", security_tool)
        drone.register_tool("file_system", FileSystemTool())
        
        print("4. Generating PoC plan for critical vulnerability...")
        if data["vulnerabilities"]:
            critical_vulns = [v for v in data["vulnerabilities"] if v["impact"] in ["High", "Medium"]]
            
            if critical_vulns:
                poc_plan_result = drone.execute(
                    "generate_poc_plan",
                    {"vulnerability": critical_vulns[0]}
                )
                
                if poc_plan_result["success"]:
                    plan = poc_plan_result["data"]
                    print(f"\n   Vulnerability: {plan['vulnerability_type']}")
                    print(f"   Impact: {plan['impact']}")
                    print()
                    print("   Exploitation Steps:")
                    for i, step in enumerate(plan["exploitation_steps"], 1):
                        print(f"   {i}. {step}")
                    print()
                    print(f"   Expected Outcome: {plan['expected_outcome']}")
                    print()
                
                print("5. Generating PoC exploit code...")
                poc_file = str(base_path / "samples" / "generated_exploit.sol")
                
                poc_result = drone.execute(
                    "write_poc_exploit",
                    {
                        "vulnerability": critical_vulns[0],
                        "output_file": poc_file,
                        "target_contract": "VulnerableBank"
                    }
                )
                
                if poc_result["success"]:
                    print(f"   ✓ PoC exploit written to: {poc_file}")
                    print()
                    
                    with open(poc_file, 'r') as f:
                        code_preview = f.read()[:500]
                    print("   Code preview:")
                    print("   " + "-" * 50)
                    for line in code_preview.split('\n')[:15]:
                        print(f"   {line}")
                    print("   ...")
                    print("   " + "-" * 50)
        
        print("\n6. Generating security report...")
        report_result = security_tool.execute(
            "get_vulnerability_report",
            vulnerabilities=data["vulnerabilities"],
            format="markdown"
        )
        
        if report_result["success"]:
            report_file = str(base_path / "samples" / "security_report.md")
            
            with open(report_file, 'w') as f:
                f.write(report_result["data"]["report"])
            
            print(f"   ✓ Security report written to: {report_file}")
        
        print("\n" + "=" * 60)
        print("Full Security Audit Demo")
        print("=" * 60)
        print()
        
        print("7. Running full security audit workflow...")
        audit_result = drone.execute(
            "full_security_audit",
            {
                "file_path": sample_contract,
                "generate_report": True,
                "report_output": str(base_path / "samples" / "full_audit_report.md"),
                "generate_poc": True,
                "poc_output": str(base_path / "samples" / "full_audit_exploit.sol")
            }
        )
        
        if audit_result["success"]:
            audit_data = audit_result["data"]
            print(f"   ✓ Full audit complete!")
            print(f"   Analysis: {audit_data['analysis']['total_issues']} issues")
            print(f"   Report generated: {audit_data.get('report_generated', False)}")
            print(f"   PoC generated: {audit_data.get('poc_generated', False)}")
            
            if audit_data.get('report_file'):
                print(f"   Report file: {audit_data['report_file']}")
            if audit_data.get('poc_file'):
                print(f"   PoC file: {audit_data['poc_file']}")
        
    else:
        print(f"   ✗ Analysis failed: {analysis_result['error']}")
        if analysis_result.get('details'):
            print(f"   Details: {analysis_result['details']}")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_security_analyzer()
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
