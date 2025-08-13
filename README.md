
STUMPZY_CRICKET/

# 📁 STUMPZY_CRICKET – Project Folder Structure

**STUMPZY_CRICKET** is an intelligent backend system built with **FastAPI**, **LangChain**, and **MongoDB**, designed to provide real-time cricket match predictions, player statistics, and answer natural language cricket-related queries using LLM tools and custom prompts.


This project is structured for scalability, modularity, and clean separation of concerns using **FastAPI**, **LangChain**, and **MongoDB**.

---

## ⚙️ Tech Stack

| Technology    | Purpose                                     |
|---------------|---------------------------------------------|
| **FastAPI**   | High-performance API framework              |
| **LangChain** | LLM orchestration, tools, agents, chains    |
| **MongoDB**   | NoSQL database for storing player/match data|
| **Pydantic**  | Data validation and schema management       |
| **Python**    | Primary language for development            |
| **Brave API** | Optional for web search integration         |
| **Open AI API** | Use LLM openAI api for Parse the Result         |
| **React**    | For FrontEnd Development       |
| **AWS**    | Amazone web Services (AWS) For Deployment       |


---
```bash

│
├── app/                            # Main application module
│   ├── __init__.py
│   ├── main.py                     # FastAPI entrypoint
│   │
│   ├── api/                        # All route handlers (FastAPI routers)
│   │   ├── __init__.py
│   │   ├── v1/                     # Versioned API structure
│   │   │   ├── __init__.py
│   │   │   ├── cricket_routes.py  # Cricket-related endpoints
│   │           
│   │
│   ├── services/                   # Business logic layer (LLM, tools, chains)
│   │   ├── __init__.py
│   │   ├── prediction.py          # Match/innings/team predictions
│   │   ├── player_stats.py        # Get player-specific info
│   │   ├── tools.py               # LangChain custom tools
│   │   └── chains.py              # LangChain chains for processing
│   │
│   ├── prompts/                   # Prompt templates for LangChain
│   │   ├── __init__.py
│   │   ├── prediction_prompt.txt
│   │   ├── stats_prompt.txt
│   │   └── trending_prompt.txt
│   │
│   ├── agents/                    # LangChain agent definitions
│   │   ├── __init__.py
│   │   └── cricket_agent.py       # Main agent orchestration
│   │
│   ├── utils/                     # Utility functions (parsers, validators, etc.)
│   │   ├── __init__.py
│   │   ├── logger.py
|   |	 └── helper.py
│   │   ├── schema_validator.py
│   │   └── search_wrapper.py      # Brave or custom search integration
│   │
|   ├── database/                    # MongoDB connection and schema logic
|   |      ├── __init__.py
|   |      ├── mongodb.py
|   |      
|   |        
│   │       
│   │        
|   |
│   └── models/                    # Pydantic models (request/response schemas)
│       ├── __init__.py
│       ├── prediction.py
│       ├── player.py
│       └── common.py
│
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_prediction.py
│
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Optional: containerization
├── README.md
└── pyproject.toml / setup.py      # Project metadata
````

---

## ✅ Import Dependencies

Add the following packages in your `requirements.txt` or install them directly:

```txt
fastapi
uvicorn[standard]
pydantic
langchain
openai                      # For LLMs (e.g., OpenAI models)
python-dotenv               # For .env config loading
httpx                       # For async HTTP calls (Brave API, etc. 
```
---

## 📌 Highlights

- 💬 **LLM-Powered Q&A**: Ask questions like “Who will win today's match?” or “What is Kohli’s average in ODIs?”
- 📊 **Smart Predictions**: Uses prompt templates and chains for match outcome analysis.
- 🧠 **LangChain Agents**: Modular tools and agents allow flexible reasoning and logic.
- 📈 **Extensible**: Easily add live-score integrations, trending topics, or voice interfaces.

---

## 🚀 Usage

This project is ready for local development, deployment, or cloud-native containerization.

Stay tuned for Postman docs, CI/CD pipelines, and more in future updates.

---

> Designed for cricket lovers, analysts, and developers who want to combine the magic of AI with the thrill of the game. 🏏✨



## ✅ Import Commands


```txt
Backend Run  -------->>  uvicorn app.main:app --reload
```
---