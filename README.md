# hackvhs
Fetch.ai x IX hackathon

To run the demo:

1. Run the profiling and RAG agents
- `agents/profiling_agent.py`
- `agents/rag_agent.py`

2. Copy the agent addresses
- rag_agent address added to `agents/orchestrator_agent.py`
- profiling_agent address added to `viz/survey.py`

3. Run orchestrator (`agents/orchestrator_agent.py`)

4. Run the frontend app
`$ streamlit run viz/app.py`