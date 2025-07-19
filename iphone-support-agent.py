import logging
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, function_tool, JobContext, WorkerOptions, cli
from livekit.agents.voice import RunContext
from livekit.agents.job import get_job_context
from livekit import api
from livekit.plugins import deepgram, silero, openai

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iphone-agent")

@dataclass
class UserData:
    customer_name: Optional[str] = None
    selected_model: Optional[str] = None
    support_issue: Optional[str] = None
    agents: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None

RunContext_T = RunContext[UserData]

class BaseAgent(Agent):
    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        print(f"🔄 ENTERING AGENT: {agent_name}")
        logger.info(f"entering {agent_name}")
        
        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        
        # Add previous agent's context if available
        if isinstance(userdata.prev_agent, Agent):
            prev_name = userdata.prev_agent.__class__.__name__
            print(f"📝 Loading context from previous agent: {prev_name}")
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True, exclude_function_call=False
            ).truncate(max_items=4)
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in truncated_chat_ctx.items if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)
        
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(tool_choice="none")

    async def _transfer_to_agent(self, name: str, context: RunContext_T) -> tuple[Agent, str]:
        userdata = context.userdata
        current_agent = context.session.current_agent
        current_name = current_agent.__class__.__name__
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent
        print(f"🔀 TRANSFERRING: {current_name} → {name.upper()}AGENT")
        return next_agent, f"Transferring to {name}."

class GreetingAgent(BaseAgent):
    def __init__(self, instructions: str = "You are Jill from iPhone support. Greet customers and understand if they need support help or want to buy a new iPhone. Route them to the appropriate agent."):
        super().__init__(instructions=instructions)

    async def on_enter(self):
        await super().on_enter()
        await self.session.say("Hi, I'm Jill from iPhone support. How can I help you today?")

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

class SupportAgent(BaseAgent):
    def __init__(self, instructions: str = "You are an iPhone technical support specialist. Help users with troubleshooting, setup issues, and iPhone questions. Be helpful and thorough."):
        super().__init__(instructions=instructions)

    @function_tool()
    async def log_support_issue(
        self, 
        issue: str,
        context: RunContext_T
    ) -> str:
        """Log the customer's support issue for reference."""
        print(f"📋 TOOL CALLED: log_support_issue - Issue: {issue}")
        userdata = context.userdata
        userdata.support_issue = issue
        return f"I've noted your issue: {issue}. Let me help you resolve this."

    @function_tool()
    async def complete_support(self, context: RunContext_T) -> str:
        """Called when the support issue has been resolved."""
        print("✅ TOOL CALLED: complete_support - returning to greeting")
        await self.session.say("Glad I could help! Is there anything else you need assistance with?")
        return await self._transfer_to_agent("greeting", context)

    @function_tool()
    async def end_support_call(self, context: RunContext_T) -> str:
        """Called when the customer is satisfied and wants to end the support call."""
        print("📞 TOOL CALLED: end_support_call - ending session")
        await self.session.say("Thank you for contacting iPhone support. Have a great day!")
        
        # Use the proper LiveKit API to end the session for everyone
        job_ctx = get_job_context()
        api_client = api.LiveKitAPI()
        await api_client.room.delete_room(api.DeleteRoomRequest(room=job_ctx.job.room.name))
        return "Support call ended."

    @function_tool()
    async def to_buying(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when customer changes their mind and wants to buy a new iPhone instead of getting support."""
        print("🔄 TOOL CALLED: to_buying - customer switching from support to buying")
        return await self._transfer_to_agent("buying", context)

class BuyingAgent(BaseAgent):
    def __init__(self, instructions: str = "You are an iPhone sales specialist. Help customers choose the right iPhone model and complete their purchase. Ask about their needs and recommend appropriate models."):
        super().__init__(instructions=instructions)

    @function_tool()
    async def select_model(
        self,
        model: str,
        context: RunContext_T
    ) -> str:
        """Called when customer selects an iPhone model."""
        print(f"📱 TOOL CALLED: select_model - Model: {model}")
        userdata = context.userdata
        userdata.selected_model = model
        return f"Great choice! You've selected the iPhone {model}."

    @function_tool()
    async def confirm_purchase(
        self,
        model: str,
        context: RunContext_T
    ) -> str:
        """Called to confirm the iPhone purchase."""
        print(f"💳 TOOL CALLED: confirm_purchase - Finalizing purchase of {model}")
        userdata = context.userdata
        userdata.selected_model = model
        await self.session.say(f"Perfect! I'm confirming your purchase of the iPhone {model}. Thank you for choosing iPhone!")
        return "Purchase confirmed. Have a great day!"

    @function_tool()
    async def end_purchase_call(self, context: RunContext_T) -> str:
        """Called when the purchase is complete and the customer wants to end the call."""
        print("📞 TOOL CALLED: end_purchase_call - ending session")
        await self.session.say("Thank you for your purchase! Your new iPhone will be shipped soon. Have a wonderful day!")
        
        # Use the proper LiveKit API to end the session for everyone
        job_ctx = get_job_context()
        api_client = api.LiveKitAPI()
        await api_client.room.delete_room(api.DeleteRoomRequest(room=job_ctx.job.room.name))
        return "Purchase call ended."

    @function_tool()
    async def to_support(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when customer changes their mind and wants technical support instead of buying a phone."""
        print("🔄 TOOL CALLED: to_support - customer switching from buying to support")
        return await self._transfer_to_agent("support", context)

def get_agent_instructions():
    """Collect custom instructions for each agent from user input."""
    print("\n" + "="*60)
    print("🤖 IPHONE SUPPORT AGENT CONFIGURATION")
    print("="*60)
    print("Customize the instructions for each agent (press Enter to use defaults):\n")
    
    # Default instructions
    default_greeting = "You are Jill from iPhone support. Greet customers and understand if they need support help or want to buy a new iPhone. Route them to the appropriate agent."
    default_support = "You are an iPhone technical support specialist. Help users with troubleshooting, setup issues, and iPhone questions. Be helpful and thorough."
    default_buying = "You are an iPhone sales specialist. Help customers choose the right iPhone model and complete their purchase. Ask about their needs and recommend appropriate models."
    
    print("1️⃣ GREETING AGENT INSTRUCTIONS:")
    print(f"   Default: {default_greeting}")
    greeting_input = input("   Custom (Press Enter to keep Default): ").strip()
    greeting_instructions = greeting_input if greeting_input else default_greeting
    
    print("\n2️⃣ SUPPORT AGENT INSTRUCTIONS:")
    print(f"   Default: {default_support}")
    support_input = input("   Custom (Press Enter to keep Default): ").strip()
    support_instructions = support_input if support_input else default_support
    
    print("\n3️⃣ BUYING AGENT INSTRUCTIONS:")
    print(f"   Default: {default_buying}")
    buying_input = input("   Custom (Press Enter to keep Default): ").strip()
    buying_instructions = buying_input if buying_input else default_buying
    
    print("\n" + "="*60)
    print("🚀 STARTING LIVEKIT AGENT WITH CUSTOM INSTRUCTIONS...")
    print("="*60)
    
    return greeting_instructions, support_instructions, buying_instructions

# Preload VAD
def prewarm(proc):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    # Get custom instructions from user input
    greeting_instructions, support_instructions, buying_instructions = get_agent_instructions()
    
    userdata = UserData()
    userdata.agents.update({
        "greeting": GreetingAgent(greeting_instructions),
        "support": SupportAgent(support_instructions),
        "buying": BuyingAgent(buying_instructions),
    })
    
    session = AgentSession[UserData](
        userdata=userdata,
        llm=openai.LLM(model="gpt-4.1-nano"),
        stt=deepgram.STT(model="nova-2"),
        tts=deepgram.TTS(model="aura-asteria-en"),
        vad=silero.VAD.load(),
        max_tool_steps=3,
    )

    await session.start(
        agent=userdata.agents["greeting"],
        room=ctx.room,
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))