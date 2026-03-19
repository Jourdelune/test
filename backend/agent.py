"""Minimal agent for debugging edit/reload with SqliteSaver."""

import sqlite3

from deepagents import create_deep_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

conn = sqlite3.connect("./checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

model = ChatOpenRouter(
    model="openai/gpt-5.4-nano",
    temperature=0.8,
)

agent = create_deep_agent(
    model=model,
    tools=[],
    subagents=[],
    backend=None,
    skills=[],
    system_prompt="You are a helpful assistant.",
    middleware=[],
    checkpointer=checkpointer,
)


async def make_graph(config):
    """Factory function called by langgraph dev for each run."""
    return agent
