# data.py
from dataclasses import dataclass, field
from typing import Optional, Dict
from livekit.agents import Agent


@dataclass
class UserData:
    customer_name: Optional[str] = None
    selected_model: Optional[str] = None
    support_issue: Optional[str] = None
    agents: Dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None
