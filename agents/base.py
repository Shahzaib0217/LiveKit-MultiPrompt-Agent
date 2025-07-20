# agents/base.py
from livekit.agents import Agent
from livekit.agents.voice import RunContext

from data import UserData

RunContext_T = RunContext[UserData]


class BaseAgent(Agent):
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
        self.session.generate_reply(tool_choice="none")

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