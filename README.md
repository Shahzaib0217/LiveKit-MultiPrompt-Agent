# LiveKit Multi Prompt Voice Agent

## Features
- Multi-customer support: Each customer can have unique agent flows, prompts, and routing.
- Dynamic agent creation: Agents and their transitions are defined in config files, not hardcoded.
- Voice interaction: Integrates with LiveKit, OpenAI, Deepgram, and Silero for LLM, STT, TTS, and VAD.
- Extensible: Add new customers, agents, or prompts by editing config files.
- Schema validation: Ensures configs are valid using JSON Schema.

## Project structure
```
├── README.md
├── requirements.txt
├── config/ (Contains JSON files)
│   ├── config_schema.json       # JSON Schema definition
│   └── agents_config.json       # Sample configuration
├── config_schema.py             # Loader & validator
├── agents/
│   ├── dynamic_agent.py         # Generic agent that reads config
│   └── factory.py               # Creates dynamic agents per customer
├── data.py                      # UserData model
├── config.py                    # Code configurations 
├── main.py                      # Entrypoint, wiring
```

## How to Run

1. **Install Dependencies**
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.tx

2. **Run Console App**
    ```bash
    python main.py console

3. **Select a Customer**
    You will be prompted to pick one from the list in agents_config.json.


## 🔧 Extending this project
You can extend this system by:

- Adding more customers in agents_config.json.
- Adding new function tool definitions and modifying dynamic_agent.py to support dynamic tool addition.

## Thought Process
- In the Retell Ai's Multi prompt Agent we can create Nodes with unique instructions and do conditional Routing.
- Here in this appraoch I have tried to achieve the same, We can define multiple agents, each with unique id, each agent is called on specific conditions `"conditions": { "onIntent": "report_issue" }` 
- One of the major parts of the Multi Prompt Agent is that Different Customers can have different configurations, this approach follows all those principles, *still there is alot of room for improvement :)*. 