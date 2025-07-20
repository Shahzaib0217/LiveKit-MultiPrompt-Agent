# LiveKit Multi Prompt Voice Agent

## Project structure
```
├── README.md
├── requirements.txt
├── config/
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