# agents/greeting.py
from livekit.agents import Agent
from livekit.agents import function_tool

from agents.base import BaseAgent, RunContext_T

class GreetingAgent(BaseAgent):
    def __init__(
        self,
        instructions: str = "You are Jill from iPhone support. Greet customers and understand if they need support help or want to buy a new iPhone. Route them to the appropriate agent.",
    ):
        super().__init__(instructions=instructions)

    async def on_enter(self):
        await super().on_enter()

    @function_tool()
    async def to_support(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user needs technical support, troubleshooting, or has questions about their current iPhone."""
        print("🛠️ TOOL CALLED: to_support - routing to technical support")
        return await self._transfer_to_agent("support", context)

    @function_tool()
    async def to_buying(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to purchase a new iPhone or learn about iPhone models."""
        print("🛒 TOOL CALLED: to_buying - routing to sales")
        return await self._transfer_to_agent("buying", context)