# agents/buying.py
from livekit.agents import Agent
from livekit.agents import function_tool
from livekit.agents.job import get_job_context
from livekit import api

from agents.base import BaseAgent, RunContext_T

class BuyingAgent(BaseAgent):
    def __init__(
        self,
        instructions: str = "You are an iPhone sales specialist. Help customers choose the right iPhone model and complete their purchase. Ask about their needs and recommend appropriate models.",
    ):
        super().__init__(instructions=instructions)

    @function_tool()
    async def select_model(self, model: str, context: RunContext_T) -> str:
        """Called when customer selects an iPhone model."""
        print(f"📱 TOOL CALLED: select_model - Model: {model}")
        userdata = context.userdata
        userdata.selected_model = model
        return f"Great choice! You've selected the iPhone {model}."

    @function_tool()
    async def confirm_purchase(self, model: str, context: RunContext_T) -> str:
        """Called to confirm the iPhone purchase."""
        print(f"💳 TOOL CALLED: confirm_purchase - Finalizing purchase of {model}")
        userdata = context.userdata
        userdata.selected_model = model
        await self.session.say(
            f"Perfect! I'm confirming your purchase of the iPhone {model}. Thank you for choosing iPhone!"
        )
        return "Purchase confirmed. Have a great day!"

    @function_tool()
    async def end_purchase_call(self, context: RunContext_T) -> str:
        """Called when the purchase is complete and the customer wants to end the call."""
        print("📞 TOOL CALLED: end_purchase_call - ending session")
        await self.session.say(
            "Thank you for your purchase! Your new iPhone will be shipped soon. Have a wonderful day!"
        )

        # Use the proper LiveKit API to end the session for everyone
        job_ctx = get_job_context()
        api_client = api.LiveKitAPI()
        await api_client.room.delete_room(
            api.DeleteRoomRequest(room=job_ctx.job.room.name)
        )
        return "Purchase call ended."

    @function_tool()
    async def to_support(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when customer changes their mind and wants technical support instead of buying a phone."""
        print("🔄 TOOL CALLED: to_support - customer switching from buying to support")
        return await self._transfer_to_agent("support", context)
