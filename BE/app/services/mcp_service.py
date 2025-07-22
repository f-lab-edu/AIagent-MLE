"""
MCP Agent 객체를 생성하는 모듈.
"""

from typing import Optional
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from contextlib import asynccontextmanager

from services.gemini import GeminiService
from core.config import mcp_config
from core.exception import CustomException, ExceptionCase

# mcp_client = MultiServerMCPClient(
#     {
#         "notion": {
#             "url": mcp_config.get_mcp_url("notion"),
#             "transport": "streamable_http",
#         }
#     }
# )


class Agent:
    def __init__(self, mcp_config: dict):
        self.client = MultiServerMCPClient(mcp_config)
        self.tools = []

    async def get_tools(self):
        if not self.tools:
            self.tools = await self.client.get_tools()
        return self.tools

    async def update_tools(self):
        tools = await self.client.get_tools()
        return tools

    @asynccontextmanager
    async def create_agent(self, response_format: Optional[BaseModel] = None):
        gemini = GeminiService()
        model = gemini.model
        tools = await self.get_tools()
        agent = create_react_agent(model, tools, response_format=response_format)

        yield agent


try:
    mcp_config_dict = {}

    # notion mcp server config
    mcp_config_dict.update(mcp_config.get_mcp_config("notion"))

    agent = Agent(mcp_config_dict)
except Exception as e:
    raise CustomException(
        exception_case=ExceptionCase.MCP_ERROR,
        detail=f"Error occured in mcp agent: {e}",
    )
