from typing import Dict, Any, Tuple
from agents.dynamic_agent import DynamicAgent

def build_customer_agents(config: Dict[str, Any], customer_id: str) -> Tuple[Dict[str, DynamicAgent], Dict[str, Any]]:
    # Find customer config
    cust = next((c for c in config['customers'] if c['customer_id'] == customer_id), None)
    if not cust:
        raise KeyError(f"Customer '{customer_id}' not found")

    agents = {}
    for ag in cust['agents']:
        agent_id = ag['id']
        instructions = ag['instructions']
        prompts = ag.get('prompts', [])
        routing = cust['routing']
        agents[agent_id] = DynamicAgent(agent_id, instructions, prompts, routing)
    return agents, cust['routing']