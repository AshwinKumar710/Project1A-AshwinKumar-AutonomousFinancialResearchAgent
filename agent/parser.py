"""
Output Parser and Trace Deconstruction for ARA-1.
Parses LLM outputs for Thought, Action, Action Input, and Final Report blocks,
validating JSON parameter schemas and error resilience.
"""

import re
import json
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("ARA.Agent.Parser")

class ReActParser:
    """
    Parses Thought-Action-Observation strings into structured execution actions.
    """
    @staticmethod
    def parse_action(text: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
        """
        Extracts (thought, action_name, action_args) from reasoning text.
        """
        thought_match = re.search(r'Thought:\s*(.*?)(?=\nAction:|\nFinal Report:|$)', text, re.DOTALL | re.IGNORECASE)
        thought = thought_match.group(1).strip() if thought_match else ""

        # Check for Final Report
        if "Final Report:" in text:
            final_report = text.split("Final Report:", 1)[1].strip()
            return thought, "FINAL_REPORT", {"report": final_report}

        action_match = re.search(r'Action:\s*([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
        if not action_match:
            return thought, None, None

        action_name = action_match.group(1).strip()

        # Parse Action Input JSON
        input_match = re.search(r'Action Input:\s*(\{.*\}|\[.*\]|"[^"]*"|\S+)', text, re.DOTALL | re.IGNORECASE)
        action_args = {}
        if input_match:
            raw_input = input_match.group(1).strip()
            try:
                action_args = json.loads(raw_input)
            except Exception:
                # Handle single unquoted string or simple key-value
                if raw_input.startswith("{") and raw_input.endswith("}"):
                    # Try cleaning up quotes
                    cleaned = re.sub(r'(\w+):', r'"\1":', raw_input)
                    try:
                        action_args = json.loads(cleaned)
                    except Exception:
                        action_args = {"query": raw_input}
                else:
                    action_args = {"query": raw_input.strip('"\'')}

        return thought, action_name, action_args
