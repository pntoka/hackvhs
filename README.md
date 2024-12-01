# 🚀 **HackVHS: Fetch.ai x IX Hackathon** 🎉

**Create your .env file**
```.env
CLIENT_KEY="apple"
PROFILING_AGENT_KEY = "kiwis"
RAG_AGENT_KEY = "chickens"
OPENAI_API_KEY="your_api_key"

# This needs to be our VECTARA_API as we have a Corpus based on documents
# from the WHO for our RAG
VECTARA_API = "zut_I9uYzUybNaZNP_5_LGJ13ylo8Reaxm7FRinmkA"
AGENTVERSE_API_KEY="your_agentverse_api_key"
```
**To run the demo:**

1. Run the profiling and RAG agents
- `agents/profiling_agent.py`
- `agents/rag_agent.py`

2. Copy the agent addresses
- rag_agent address added to `agents/orchestrator_agent.py`
- profiling_agent address added to `viz/survey.py`

3. Run orchestrator (`agents/orchestrator_agent.py`)

4. Run the frontend app
```
$ streamlit run viz/app.py
```
