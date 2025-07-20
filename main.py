import json
from pathlib import Path

from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, silero, openai

from config_schema import load_and_validate_config
from agents.factory import build_customer_agents
from data import UserData
from config import LLM_MODEL, STT_MODEL, TTS_MODEL

async def entrypoint(ctx: JobContext, customer_id: str, cfg_path: str):
    # Load and validate configuration
    config = load_and_validate_config(cfg_path)
    agents, routing = build_customer_agents(config, customer_id)

    # Prepare user data
    userdata = UserData()
    userdata.agents = agents
    userdata.routing = routing

    # Initialize the LiveKit agent session
    session = AgentSession[UserData](
        userdata=userdata,
        llm=openai.LLM(model=LLM_MODEL),
        stt=deepgram.STT(model=STT_MODEL),
        tts=deepgram.TTS(model=TTS_MODEL),
        vad=silero.VAD.load(),
        max_tool_steps=3,
    )

    # Start with the greeting agent
    start_agent = agents.get('greeting')
    await session.start(agent=start_agent, room=ctx.room)


if __name__ == "__main__":
    # Load the config file once to extract customers
    cfg_path = "config/agents_config.json"
    try:
        config = json.loads(Path(cfg_path).read_text())
        customers = config.get("customers", [])
        if not customers:
            raise ValueError("No customers found in config.")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        exit(1)

    # Show list of customers
    print("📋 Available Customers:")
    for idx, cust in enumerate(customers):
        print(f"  [{idx+1}] {cust['customer_id']}")

    # Get selection
    try:
        choice = int(input("Select a customer by number: ").strip())
        customer = customers[choice - 1]["customer_id"]
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        exit(1)

    # Launch agent for selected customer
    def start_fn(ctx):
        return entrypoint(ctx, customer, cfg_path)

    cli.run_app(WorkerOptions(entrypoint_fnc=start_fn))