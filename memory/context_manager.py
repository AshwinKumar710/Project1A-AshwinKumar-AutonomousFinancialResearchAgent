"""
Short-Term Working Memory & Context Manager for ARA-1.
Manages LLM context budgeting (Section A8.2: 40% Primary Data, 30% Supporting Evidence,
20% System Prompt & Tools, 10% Generation Buffer) and progressive summarization.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ARA.Memory.ContextManager")

class TokenBudgeter:
    """
    Allocates and monitors token limits across prompt zones.
    """
    def __init__(self, max_context_tokens: int = 128000):
        self.max_tokens = max_context_tokens
        # Budget distribution based on Section A8.2 token budgeting principles
        self.budget_primary_data = int(max_context_tokens * 0.40)      # 40%
        self.budget_supporting_data = int(max_context_tokens * 0.30)   # 30%
        self.budget_system_tools = int(max_context_tokens * 0.20)      # 20%
        self.budget_generation = int(max_context_tokens * 0.10)        # 10%

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation: ~4 chars per token for financial text."""
        return max(1, len(text) // 4)


class ContextManager:
    """
    Manages the active session working memory, scratchpad, thought traces,
    and implements progressive summarization when token limits approach threshold.
    """
    def __init__(self, max_active_steps: int = 12, token_limit: int = 128000):
        self.max_active_steps = max_active_steps
        self.budgeter = TokenBudgeter(token_limit)
        
        # Working memory state
        self.query: str = ""
        self.plan: List[str] = []
        self.completed_steps: List[str] = []
        self.scratchpad: List[Dict[str, Any]] = [] # Thought-Action-Observation trace
        self.accumulated_data: Dict[str, Any] = {} # Keyed by tool/topic
        self.summarized_history: str = ""
        self.iteration_count: int = 0

    def initialize_session(self, query: str, plan: Optional[List[str]] = None):
        """Resets and initializes a fresh research session context."""
        self.query = query
        self.plan = plan or []
        self.completed_steps = []
        self.scratchpad = []
        self.accumulated_data = {}
        self.summarized_history = ""
        self.iteration_count = 0
        logger.info("Initialized research session: '%s'", query)

    def add_trace(self, thought: str, action: str, observation: Any):
        """Records a Thought-Action-Observation cycle."""
        self.iteration_count += 1
        trace_entry = {
            "step": self.iteration_count,
            "thought": thought,
            "action": action,
            "observation": observation
        }
        self.scratchpad.append(trace_entry)
        logger.debug("Added trace step %d: Action=%s", self.iteration_count, action)

        # Check if we need progressive summarization
        if len(self.scratchpad) > self.max_active_steps:
            self._compress_older_traces()

    def add_data(self, key: str, data: Any):
        """Adds structured data gathered during execution."""
        self.accumulated_data[key] = data

    def _compress_older_traces(self):
        """
        Progressively summarizes older trace steps into a compact historical summary.
        Keeps the most recent steps uncompressed for immediate reasoning.
        """
        logger.info("Triggering progressive summarization of working memory traces...")
        steps_to_compress = self.scratchpad[:-5] # Keep last 5 steps in full fidelity
        
        summary_lines = []
        for step in steps_to_compress:
            obs_preview = str(step["observation"])[:120].replace("\n", " ")
            summary_lines.append(
                f"- Step {step['step']}: Reasoned '{step['thought'][:80]}...' -> Executed {step['action']} -> Result: {obs_preview}..."
            )
        
        compressed_text = "\n".join(summary_lines)
        if self.summarized_history:
            self.summarized_history += "\n" + compressed_text
        else:
            self.summarized_history = compressed_text

        # Retain only recent steps in active scratchpad
        self.scratchpad = self.scratchpad[-5:]

    def get_working_context(self) -> Dict[str, Any]:
        """
        Assembles the optimized working memory payload for LLM reasoning.
        """
        return {
            "query": self.query,
            "plan": self.plan,
            "iteration": self.iteration_count,
            "summarized_past_steps": self.summarized_history,
            "active_trace_scratchpad": self.scratchpad,
            "gathered_sources": list(self.accumulated_data.keys()),
            "estimated_token_usage": self.estimate_current_token_usage()
        }

    def estimate_current_token_usage(self) -> Dict[str, int]:
        scratchpad_str = str(self.scratchpad)
        data_str = str(self.accumulated_data)
        summary_str = self.summarized_history
        
        used_scratch = self.budgeter.estimate_tokens(scratchpad_str)
        used_data = self.budgeter.estimate_tokens(data_str)
        used_summary = self.budgeter.estimate_tokens(summary_str)
        
        return {
            "total_estimated_tokens": used_scratch + used_data + used_summary,
            "scratchpad_tokens": used_scratch,
            "accumulated_data_tokens": used_data,
            "summary_tokens": used_summary,
            "budget_limit": self.budgeter.max_tokens
        }
