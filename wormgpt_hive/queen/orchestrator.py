import json
from typing import Any, Dict, List, Optional
from openai import OpenAI

from ..drones.base_drone import DroneRegistry, MissionStep
from ..shared.config import (
    FIREWORKS_API_KEY,
    OPENROUTER_BASE_URL,
    QUEEN_MODEL,
    HTTP_REFERER,
    QUEEN_SYSTEM_PROMPT,
    REFLECTION_PROMPT_TEMPLATE,
    HUMAN_FEEDBACK_PROMPT_TEMPLATE,
)
from ..shared.state_manager import StateManager
from ..shared.knowledge_graph import KnowledgeGraph
from ..queen.message_bus import MessageBus



class QueenOrchestrator:
    """Supreme Queen of the WormGPT Hive Mind. Plans missions, delegates to drones, reflects on results, and self-corrects."""

    def __init__(self, registry: DroneRegistry, state_manager: StateManager, queen_id: str = "default_queen", message_bus: Optional[MessageBus] = None, queen_registry = None):
        self.registry = registry
        self.state_manager = state_manager
        self.client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=OPENROUTER_BASE_URL)
        self.client.default_model = QUEEN_MODEL
        self.knowledge_graph = KnowledgeGraph()
        self.queen_id = queen_id
        self.message_bus = message_bus
        self.queen_registry = queen_registry
        self.current_mission = None
        self.mission_steps = []
        self.step_index = 0

    def execute_mission(self, goal: str, verbose: bool = True) -> Dict[str, Any]:
        if verbose:
            print(f"\n{'='*60}")
            print("🐝 QUEEN: Initiating new mission")
            print(f"GOAL: {goal}")
            print(f"{'='*60}\n")

        mission_id = f"mission_{len(self.state_manager.get_mission_history()) + 1}"
        self.knowledge_graph.add_node(mission_id, "mission", attributes=self._serialize_attributes({"goal": goal}))
        
        self.current_mission = {
            "id": mission_id,
            "goal": goal,
            "status": "planning",
            "steps": [],
            "result": None,
        }

        capabilities = self.registry.get_capabilities_summary()

        plan = self._generate_plan(goal, capabilities)

        if not plan:
            self._update_knowledge_graph(mission_id, {"status": "failed", "error": "Failed to generate plan"})
            return {
                "success": False,
                "error": "Failed to generate plan",
                "mission": self.current_mission,
            }

        self.mission_steps = plan
        self.current_mission["steps"] = [step.to_dict() for step in plan]
        self.current_mission["status"] = "executing"

        if verbose:
            print(f"\n📋 QUEEN: Mission plan created with {len(plan)} steps\n")
        
        for idx, step in enumerate(plan):
            self.step_index = idx
            
            step_id = f"{mission_id}_step_{step.step_id}"
            self.knowledge_graph.add_node(step_id, "step", attributes=self._serialize_attributes(step.to_dict()))
            self.knowledge_graph.add_edge(mission_id, step_id, "has_step")

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
                    if step.result and "details" in step.result:
                        print(f"  DETAILS: {step.result['details']}")

            self._update_knowledge_graph(step_id, step.to_dict())

            if step.status == "failed":
                reflection = self._reflect_on_failure(step)

                if not isinstance(reflection, dict):
                    if verbose:
                        print("\n⚠️  QUEEN: Reflection failed, continuing mission...\n")
                    continue

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
                        plan = plan[: idx + 1] + remaining_steps
                        self.mission_steps = plan

                elif reflection.get("next_action") == "continue":
                    if verbose:
                        print(
                            "\n⚠️  QUEEN: Non-critical error, continuing mission...\n"
                        )
                    continue

        self.current_mission["status"] = "completed"

        success_count = sum(1 for s in plan if s.status == "completed")
        self.current_mission["result"] = {
            "total_steps": len(plan),
            "successful_steps": success_count,
            "failed_steps": len(plan) - success_count,
        }
        
        self._update_knowledge_graph(mission_id, {"status": "completed", "result": self.current_mission["result"]})
        self.knowledge_graph.save_graph("knowledge_graph.graphml")

        self.state_manager.add_mission(self.current_mission)

        if verbose:
            print(f"\n{'='*60}")
            print("🏆 MISSION COMPLETE")
            print(f"Success: {success_count}/{len(plan)} steps")
            print(f"{'='*60}\n")

        return {
            "success": success_count == len(plan),
            "mission": self.current_mission,
            "steps": [s.to_dict() for s in plan],
        }

    def _receive_messages_from_bus(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not self.message_bus:
            return {"success": False, "error": "Message bus not initialized."}
        
        messages = self.message_bus.receive_messages(self.queen_id)
        return {"success": True, "messages": messages}

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "send_message": {
                "description": "Sends a message to another Queen.",
                "parameters": [
                    {"name": "recipient_queen_id", "type": "str", "description": "The ID of the recipient Queen."},
                    {"name": "message", "type": "Dict[str, Any]", "description": "The message to send."}
                ]
            },
            "check_mailbox": {
                "description": "Checks for and retrieves messages from the Queen's mailbox.",
                "parameters": []
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "send_message":
            return self.send_message(parameters)
        elif action == "check_mailbox":
            return self._receive_messages_from_bus(parameters)
        else:
            if "goal" in parameters:
                return self.execute_mission(parameters["goal"])
            else:
                return {"success": False, "error": "Missing 'goal' parameter for execute_mission."}

    def send_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not self.message_bus:
            return {"success": False, "error": "Message bus not initialized."}
        
        recipient_queen_id = parameters.get("recipient_queen_id")
        message = parameters.get("message")

        if not recipient_queen_id or not message:
            return {"success": False, "error": "Missing 'recipient_queen_id' or 'message' parameter."}

        message["sender_queen_id"] = self.queen_id
        self.message_bus.send_message(recipient_queen_id, message)
        return {"success": True, "message": f"Message sent to {recipient_queen_id}."}


    def _generate_plan(self, goal: str, capabilities: Dict[str, Any]) -> Optional[List[MissionStep]]:
        try:
            # If the goal is to process messages, first check the mailbox
            if goal == "check mailbox and execute tasks":
                mailbox_result = self._receive_messages_from_bus({})
                if mailbox_result["success"] and mailbox_result.get("messages"):
                    messages = mailbox_result["messages"]
                    
                    # For simplicity, process the first message for now
                    task_message = messages[0]
                    task_payload = task_message.get("message", {})
                    sender_queen_id = task_message.get("sender_queen_id", self.queen_id) # Default to self if no sender

                    if task_payload and task_payload.get("task"):
                        task_name = task_payload["task"]
                        
                        if task_name == "port_scan":
                            target = task_payload.get("target", "localhost")
                            
                            plan_steps = [
                                MissionStep(
                                    step_id=1,
                                    action="ReconDrone.port_scan",
                                    parameters={"target": target},
                                    reasoning=f"Execute port scan as requested by {sender_queen_id}"
                                ),
                                MissionStep(
                                    step_id=2,
                                    action=f"{self.queen_id}.send_message",
                                    parameters={
                                        "recipient_queen_id": sender_queen_id,
                                        "message": {"status": "completed", "task": "port_scan", "target": target, "result": "Port scan completed. Check ReconDrone output."}
                                    },
                                    reasoning=f"Report port scan completion to {sender_queen_id}"
                                )
                            ]
                            return plan_steps
                        else:
                            # If task is not recognized, report back to sender
                            return [MissionStep(
                                step_id=1,
                                action=f"{self.queen_id}.send_message",
                                parameters={
                                    "recipient_queen_id": sender_queen_id,
                                    "message": {"status": "failed", "details": f"Unknown task: {task_name}", "original_message": task_payload}
                                },
                                reasoning="Report back unknown task to sender Queen"
                            )]

                    return [MissionStep(
                        step_id=1,
                        action=f"{self.queen_id}.send_message",
                        parameters={
                            "recipient_queen_id": sender_queen_id,
                            "message": {"status": "failed", "details": "Received empty or malformed task message", "original_message": task_payload}
                        },
                        reasoning="Report back malformed message to sender Queen"
                    )]
                else:
                    return [MissionStep(
                        step_id=1,
                        action=f"{self.queen_id}.send_message", # Send to self for reporting
                        parameters={
                            "recipient_queen_id": self.queen_id, 
                            "message": {"status": "completed", "details": "No new messages in mailbox."}
                        },
                        reasoning="Mailbox is empty, no tasks to execute."
                    )]

            # If not a message processing goal, proceed with normal plan generation
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
                    {"role": "user", "content": user_prompt},
                ],
                extra_headers={"HTTP-Referer": HTTP_REFERER},
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
                    reasoning=step_dict["reasoning"],
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

            target_name, action_name = action_parts

            # Check if the target is a queen
            if self.queen_registry and self.queen_registry.get_queen(target_name):
                queen = self.queen_registry.get_queen(target_name)
                if not queen:
                    step.mark_failed(f"Queen not found: {target_name}")
                    return step.to_dict()
                
                result = queen.execute(action_name, step.parameters)
            else: # Assume it's a drone
                drone = self.registry.get_drone(target_name)
                if not drone:
                    step.mark_failed(f"Drone not found: {target_name}")
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
                observation=step.observation or "No observation",
            )
            response = self.client.chat.completions.create(
                model=QUEEN_MODEL,
                messages=[
                    {"role": "system", "content": QUEEN_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                extra_headers={"HTTP-Referer": HTTP_REFERER},
            )

            reflection_json = response.choices[0].message.content.strip()

            if "```json" in reflection_json:
                reflection_json = (
                    reflection_json.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in reflection_json:
                reflection_json = (
                    reflection_json.split("```")[1].split("```")[0].strip()
                )

            return json.loads(reflection_json)

        except Exception as e:
            print(f"Reflection failed: {e}")
            return {"next_action": "continue"}

    def _request_human_feedback(self, question: str) -> str:
        prompt = HUMAN_FEEDBACK_PROMPT_TEMPLATE.format(
            mission_goal=self.current_mission["goal"],
            situation=f"Step {self.step_index + 1} failed",
            question=question,
        )

        print(f"\n{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return input("Your response: ").strip()

    def _parse_plan_from_llm(
        self, plan_data: List[Dict[str, Any]]
    ) -> List[MissionStep]:
        steps = []
        for step_dict in plan_data:
            step = MissionStep(
                step_id=step_dict["step_id"],
                action=step_dict["action"],
                parameters=step_dict["parameters"],
                reasoning=step_dict["reasoning"],
            )
            steps.append(step)
        return steps

    def _serialize_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        serialized_attributes = {}
        for key, value in attributes.items():
            if isinstance(value, (dict, list)):
                serialized_attributes[key] = json.dumps(value)
            elif value is None:
                serialized_attributes[key] = ""
            else:
                serialized_attributes[key] = value
        return serialized_attributes

    def _update_knowledge_graph(self, node_id: str, attributes: Dict[str, Any]):
        """Helper to update a node's attributes in the knowledge graph."""
        if node_id in self.knowledge_graph.graph:
            serialized_attributes = self._serialize_attributes(attributes)
            for key, value in serialized_attributes.items():
                self.knowledge_graph.graph.nodes[node_id][key] = value

    def get_mission_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.state_manager.get_mission_history(limit)
