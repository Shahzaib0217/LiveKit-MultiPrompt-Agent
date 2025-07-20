# agents/base.py
from livekit.agents import Agent
from livekit.agents.voice import RunContext
from livekit.agents.job import get_job_context
from livekit import api
from livekit.api.twirp_client import TwirpError

from data import UserData
from config import configure_logging

RunContext_T = RunContext[UserData]


class BaseAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a shared LiveKit API client for this agent
        self._api_client = api.LiveKitAPI()
        self.logger = configure_logging()

    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        print(f"🔄 ENTERING AGENT: {agent_name}")

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
            items_copy = [
                item for item in truncated_chat_ctx.items if item.id not in existing_ids
            ]
            chat_ctx.items.extend(items_copy)

        await self.update_chat_ctx(chat_ctx)
        await self.session.generate_reply(tool_choice="none")

    async def _transfer_to_agent(
        self, name: str, context: RunContext_T
    ) -> tuple[Agent, str]:
        userdata = context.userdata
        current_agent = context.session.current_agent
        current_name = current_agent.__class__.__name__
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent
        print(f"🔀 TRANSFERRING: {current_name} → {name.upper()}AGENT")
        return next_agent, f"Transferring to {name}."

    async def _end_session(self):
        job_ctx = get_job_context()
        try:
            # Try deleting the room for everyone
            await self._api_client.room.delete_room(
                api.DeleteRoomRequest(room=job_ctx.job.room.name)
            )
        except TwirpError as e:
            self.logger.warning("Room delete failed (might already be gone): %s", e)
        finally:
            # Cleanly close the HTTP client session
            await self._api_client.aclose()

    async def on_unrecognized(self, text: str):
        await self.session.say("Sorry, I didn’t quite get that. Could you rephrase?")