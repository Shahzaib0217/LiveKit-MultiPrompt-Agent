# agents/buying.py
from livekit.agents import Agent
from livekit.agents import function_tool

from agents.base import BaseAgent, RunContext_T

class SupportAgent(BaseAgent):
    def __init__(
        self,
        instructions: str = "You are an iPhone technical support specialist. Help users with troubleshooting, setup issues, and iPhone questions. Be helpful and thorough.",
    ):
        super().__init__(instructions=instructions)

    @function_tool()
    async def log_support_issue(self, issue: str, context: RunContext_T) -> str:
        """Log the customer's support issue for reference."""
        print(f"📋 TOOL CALLED: log_support_issue - Issue: {issue}")
        userdata = context.userdata
        userdata.support_issue = issue
        return f"I've noted your issue: {issue}. Let me help you resolve this."
        """
        Or we coulld do
            # Prompt for next step
            await self.session.say(
                f"Got it — you’re having: “{issue}”. Would you like me to walk through some troubleshooting steps, or connect you with a human agent?"
            )
            return self, "awaiting_next_step"
        """

    @function_tool()
    async def complete_support(self, context: RunContext_T) -> str:
        """Called when the support issue has been resolved."""
        print("✅ TOOL CALLED: complete_support - returning to greeting")
        await self.session.say(
            "Glad I could help! Is there anything else you need assistance with?"
        )
        return await self._transfer_to_agent("greeting", context)

    @function_tool()
    async def end_support_call(self, context: RunContext_T) -> str:
        """Called when the customer is satisfied and wants to end the support call."""
        print("📞 TOOL CALLED: end_support_call - ending session")
        await self.session.say(
            "Thank you for contacting iPhone support. Have a great day!"
        )

        await self._end_session()
        return "Support call ended."

    @function_tool()
    async def to_buying(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when customer changes their mind and wants to buy a new iPhone instead of getting support."""
        print("🔄 TOOL CALLED: to_buying - customer switching from support to buying")
        return await self._transfer_to_agent("buying", context)
