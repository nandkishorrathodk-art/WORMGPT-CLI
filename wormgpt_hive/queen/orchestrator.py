import json
from typing import Any, Dict, List, Optional
from openai import OpenAI

from ..drones.base_drone import DroneRegistry, MissionStep
from ..shared.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    QUEEN_MODEL,
    HTTP_REFERER,
    QUEEN_SYSTEM_PROMPT,
    REFLECTION_PROMPT_TEMPLATE,
    HUMAN_FEEDBACK_PROMPT_TEMPLATE
)
from ..shared.state_manager import StateManager


class QueenOrchestrator:
    """Supreme Queen of the WormGPT Hive Mind. Plans missions, delegates to drones, reflects on results, and self-corrects."""
    
    def __init__(self, registry: DroneRegistry, state_manager: StateManager):
        self.registry = registry
        self.state_manager = state_manager
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
        self.current_mission = None
        self.mission_steps = []
        self.step_index = 0
    
    def execute_mission(self, goal: str, verbose: bool = True) -> Dict[str, Any]:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🐝 QUEEN: Initiating new mission")
            print(f"GOAL: {goal}")
            print(f"{'='*60}\n")
        
        self.current_mission = {
            "goal": goal,
            "status": "planning",
            "steps": [],
            "result": None
        }
        
        capabilities = self.registry.get_capabilities_summary()
        
        plan = self._generate_plan(goal, capabilities)
        
        if not plan:
            return {
                "success": False,
                "error": "Failed to generate mission plan",
                "mission": self.current_mission
            }
        
        self.mission_steps = plan
        self.current_mission["steps"] = [step.to_dict() for step in plan]
        self.current_mission["status"] = "executing"
        
        if verbose:
            print(f"\n📋 QUEEN: Mission plan created with {len(plan)} steps\n")
        
        for idx, step in enumerate(plan):
            self.step_index = idx
            
            if verbose:
                print(f"\n{'─'*60}")
                print(f"STEP {step.step_id}: {step.action}")
                print(f"REASONING: {step.reasoning}")
                print(f"{'─'*60}")
            
            result = self._execute_step(step)
            
            if verbose:
                if step.status == "completed":
                    print(f"✓ SUCCESS: {step.observation}")
                else:
                    print(f"✗ FAILED: {step.observation}")
            
            if step.status == "failed":
                reflection = self._reflect_on_failure(step)
                
                if reflection.get("next_action") == "request_human_feedback":
                    feedback = self._request_human_feedback(
                        reflection.get("question", "How should I proceed?")
                    )
                    if verbose:
                        print(f"\n💬 HUMAN FEEDBACK: {feedback}\n")
                    
                elif reflection.get("next_action") == "replan":
                    if verbose:
                        print("\n🔄 QUEEN: Re-planning mission...\n")
                    revised_plan = reflection.get("revised_plan", [])
                    if revised_plan:
                        remaining_steps = self._parse_plan_from_llm(revised_plan)
                        plan = plan[:idx+1] + remaining_steps
                        self.mission_steps = plan
                
                elif reflection.get("next_action") == "continue":
                    if verbose:
                        print("\n⚠️  QUEEN: Non-critical error, continuing mission...\n")
                    continue
        
        self.current_mission["status"] = "completed"
        
        success_count = sum(1 for s in plan if s.status == "completed")
        self.current_mission["result"] = {
            "total_steps": len(plan),
            "successful_steps": success_count,
            "failed_steps": len(plan) - success_count
        }
        
        self.state_manager.add_mission(self.current_mission)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"🏆 MISSION COMPLETE")
            print(f"Success: {success_count}/{len(plan)} steps")
            print(f"{'='*60}\n")
        
        return {
            "success": success_count == len(plan),
            "mission": self.current_mission,
            "steps": [s.to_dict() for s in plan]
        }
    
    def _generate_plan(self, goal: str, capabilities: Dict[str, Any]) -> Optional[List[MissionStep]]:
        try:
            capabilities_str = json.dumps(capabilities, indent=2)
            
            user_prompt = f"""MISSION GOAL: {goal}

AVAILABLE CAPABILITIES:
{capabilities_str}

Generate a detailed step-by-step plan to achieve this mission. Output ONLY a JSON array of steps in this exact format:
[
  {{
    "step_id": 1,
    "action": "DroneName.action_name",
    "parameters": {{"param1": "value1"}},
    "reasoning": "Why this step is necessary"
  }}
]

Be specific with drone names and action names based on the available capabilities."""
            
            response = self.client.chat.completions.create(
                model=QUEEN_MODEL,
                messages=[
                    {"role": "system", "content": QUEEN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                extra_headers={
                    "HTTP-Referer": HTTP_REFERER
                }
            )
            
            plan_json = response.choices[0].message.content.strip()
            
            if "```json" in plan_json:
                plan_json = plan_json.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_json:
                plan_json = plan_json.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(plan_json)
            
            steps = []
            for step_dict in plan_data:
                step = MissionStep(
                    step_id=step_dict["step_id"],
                    action=step_dict["action"],
                    parameters=step_dict["parameters"],
                    reasoning=step_dict["reasoning"]
                )
                steps.append(step)
            
            return steps
        
        except Exception as e:
            print(f"Failed to generate plan: {e}")
            return None
    
    def _execute_step(self, step: MissionStep) -> Dict[str, Any]:
        try:
            action_parts = step.action.split(".")
            if len(action_parts) != 2:
                step.mark_failed(f"Invalid action format: {step.action}")
                return step.to_dict()
            
            drone_name, action_name = action_parts
            
            drone = self.registry.get_drone(drone_name)
            if not drone:
                step.mark_failed(f"Drone not found: {drone_name}")
                return step.to_dict()
            
            result = drone.execute(action_name, step.parameters)
            
            if result.get("success"):
                observation = result.get("message", "Action completed successfully")
                step.mark_completed(observation, result.get("data"))
            else:
                error = result.get("error", "Unknown error")
                step.mark_failed(f"Error: {error}", result.get("details"))
            
            return step.to_dict()
        
        except Exception as e:
            step.mark_failed(f"Execution error: {str(e)}")
            return step.to_dict()
    
    def _reflect_on_failure(self, step: MissionStep) -> Dict[str, Any]:
        try:
            prompt = REFLECTION_PROMPT_TEMPLATE.format(
                mission_goal=self.current_mission["goal"],
                current_step=step.step_id,
                action=step.action,
                parameters=json.dumps(step.parameters),
                observation=step.observation or "No observation"
            )
            
            response = self.client.chat.completions.create(
                model=QUEEN_MODEL,
                messages=[
                    {"role": "system", "content": QUEEN_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": HTTP_REFERER
                }
            )
            
            reflection_json = response.choices[0].message.content.strip()
            
            if "```json" in reflection_json:
                reflection_json = reflection_json.split("```json")[1].split("```")[0].strip()
            elif "```" in reflection_json:
                reflection_json = reflection_json.split("```")[1].split("```")[0].strip()
            
            return json.loads(reflection_json)
        
        except Exception as e:
            print(f"Reflection failed: {e}")
            return {"next_action": "continue"}
    
    def _request_human_feedback(self, question: str) -> str:
        prompt = HUMAN_FEEDBACK_PROMPT_TEMPLATE.format(
            mission_goal=self.current_mission["goal"],
            situation=f"Step {self.step_index + 1} failed",
            question=question
        )
        
        print(f"\n{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")
        
        return input("Your response: ").strip()
    
    def _parse_plan_from_llm(self, plan_data: List[Dict[str, Any]]) -> List[MissionStep]:
        steps = []
        for step_dict in plan_data:
            step = MissionStep(
                step_id=step_dict["step_id"],
                action=step_dict["action"],
                parameters=step_dict["parameters"],
                reasoning=step_dict["reasoning"]
            )
            steps.append(step)
        return steps
    
    def get_mission_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.state_manager.get_mission_history(limit)
