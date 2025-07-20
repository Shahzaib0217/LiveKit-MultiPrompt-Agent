from livekit.agents import Agent
from livekit.agents import function_tool
from livekit.agents.voice import RunContext
from data import UserData

RunCtx = RunContext[UserData]

class DynamicAgent(Agent):
    def __init__(self, agent_id: str, instructions: str, prompts: list, routing: dict):
        super().__init__(instructions=instructions)
        self.agent_id = agent_id
        # Build prompts dict, support both 'name' and 'promptId' keys
        self.prompts = {}
        for p in prompts:
            key = p.get('name') or p.get('promptId')
            if not key:
                continue
            self.prompts[key] = p
        self.routing = routing.get(agent_id, {}).get('transitions', {})

    async def on_enter(self) -> None:
        await super().on_enter()
        # If there's a prompt named 'welcome' or the first prompt, send it
        if 'welcome' in self.prompts:
            tmpl = self.prompts['welcome'].get('template') or self.prompts['welcome'].get('content')
            await self.session.say(tmpl)
        elif self.prompts:
            # send the first prompt
            first = next(iter(self.prompts.values()))
            tmpl = first.get('template') or first.get('content')
            await self.session.say(tmpl)

    @function_tool()
    async def route(self, event: str, context: RunCtx):
        # Generic routing tool: transfers based on event name
        target = self.routing.get(event)
        if not target:
            return f"No transition defined for '{event}' in agent '{self.agent_id}'."
        return await self._transfer_to_agent(target, context)