# agents/greeting.py
from livekit.agents import Agent
from livekit.agents import function_tool

from agents.base import BaseAgent, RunContext_T

class GreetingAgent(BaseAgent):
    def __init__(
        self,
        instructions: str = (
            "Ask if they need support help or want to buy a new iPhone, "
            "and route them accordingly."
        ),
    ):
        super().__init__(instructions=instructions)


    async def on_enter(self):
        # Always load context & history
        await super().on_enter()


    @function_tool()
    async def set_name(self, name: str, context: RunContext_T) -> str:
        """Capture the user’s name and move on to the main greeting."""
        context.userdata.customer_name = name
        return (
            f"Thanks, {name}! "
            "Would you like help troubleshooting your current iPhone, "
            "or are you looking to learn about and purchase a new model?"
        )

    @function_tool()
    async def to_support(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user needs technical support, troubleshooting, or has questions about their current iPhone."""
        print("🛠️ TOOL CALLED: to_support - routing to technical support")
        return await self._transfer_to_agent("support", context)

    @function_tool()
    async def to_buying(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to purchase a new iPhone or learn about iPhone models."""
        print("🛠️ TOOL CALLED: to_buying - routing to sales")
        return await self._transfer_to_agent("buying", context)