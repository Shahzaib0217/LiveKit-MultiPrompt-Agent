# main.py
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, silero, openai
from config import configure_logging, LLM_MODEL, STT_MODEL, TTS_MODEL
from data import UserData
from agents.greeting import GreetingAgent
from agents.support import SupportAgent
from agents.buying import BuyingAgent

logger = configure_logging()


def get_agent_instructions():
    """Collect custom instructions for each agent from user input."""
    print("\n" + "=" * 60)
    print("🤖 IPHONE SUPPORT AGENT CONFIGURATION")
    print("=" * 60)
    print("Customize the instructions for each agent (press Enter to use defaults):\n")

    # Default instructions
    default_greeting = "You are Jill from iPhone Customer Service. Greet and Welcome customers and ask their name"
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

    print("\n" + "=" * 60)
    print("🚀 STARTING LIVEKIT AGENT WITH CUSTOM INSTRUCTIONS...")
    print("=" * 60)

    return greeting_instructions, support_instructions, buying_instructions


async def entrypoint(ctx: JobContext):
    greeting_ins, support_ins, buying_ins = get_agent_instructions()
    userdata = UserData()
    userdata.agents = {
        "greeting": GreetingAgent(greeting_ins),
        "support": SupportAgent(support_ins),
        "buying": BuyingAgent(buying_ins),
    }

    session = AgentSession[UserData](
        userdata=userdata,
        llm=openai.LLM(model=LLM_MODEL),
        stt=deepgram.STT(model=STT_MODEL),
        tts=deepgram.TTS(model=TTS_MODEL),
        vad=silero.VAD.load(),
        max_tool_steps=3,
    )
    await session.start(agent=userdata.agents["greeting"], room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))