"""
═══════════════════════════════════════════════════════════════════════
MCP TOOL CALLING — Agent sử dụng tools từ MCP Server
═══════════════════════════════════════════════════════════════════════

Approach này:
  1. Agent KHÔNG biết tools là gì → chỉ biết có MCP Server
  2. MCP Client kết nối tới MCP Server và DISCOVER tools tự động
  3. Tools discovered được convert thành LangChain Tool objects
  4. LangGraph agent sử dụng tools giống như Native (từ góc nhìn LLM)

Điểm khác biệt quan trọng:
  • Tools được DYNAMIC DISCOVERY — không hard-code trong agent
  • Agent có thể dùng tools từ NHIỀU MCP Servers khác nhau
  • MCP Server có thể chạy trên máy khác (remote via HTTP/SSE)
  • Có thể thêm/bớt tools mà KHÔNG cần sửa code agent

Flow:
  ┌─────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────┐
  │  User   │────▶│   Agent   │────▶│ MCP Client  │────▶│   MCP    │
  │  Query  │     │  (Host)   │     │ (discover)  │     │  Server  │
  └─────────┘     └─────┬─────┘     └──────┬──────┘     └──────────┘
                        │                   │
                        │   tools list      │
                        │◀──────────────────┘
                        │
                  ┌─────▼─────┐
                  │   LLM +   │
                  │  tools    │
                  └─────┬─────┘
                        │  tool_call
                  ┌─────▼─────┐     ┌──────────┐
                  │   MCP     │────▶│   MCP    │    ← Execute qua MCP Server
                  │  Client   │◀────│  Server  │
                  └─────┬─────┘     └──────────┘
                        │
                        ▼
                  Final Response
"""

import asyncio
import sys
import os

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Đảm bảo import được shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_MODEL_NAME


# ═══════════════════════════════════════════════════════════════
# MCP Client Configuration
# ═══════════════════════════════════════════════════════════════
# Cấu hình kết nối tới MCP Server
# Transport "stdio": chạy MCP server như subprocess
# Trong production có thể dùng "http" hoặc "sse" cho remote servers

def get_mcp_config():
    """Trả về cấu hình MCP Server connections.

    Có thể kết nối NHIỀU servers cùng lúc — mỗi server expose tools riêng.
    Đây là sức mạnh chính của MCP: aggregation từ nhiều nguồn.
    """
    # Đường dẫn tới MCP server script
    server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mcp_server.py"
    )

    # Project root (nơi có pyproject.toml)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return {
        # Server 1: Agent Tool Server (local, stdio transport)
        # Dùng "uv run" để đảm bảo subprocess dùng đúng venv do uv quản lý
        "agent_tools": {
            "command": "uv",
            "args": ["run", "--directory", project_root, "python", server_script],
            "transport": "stdio",
        },
        # Có thể thêm nhiều servers khác:
        # "github_server": {
        #     "url": "http://localhost:8001/mcp",
        #     "transport": "http",
        # },
        # "database_server": {
        #     "command": "uv",
        #     "args": ["run", "python", "db_mcp_server.py"],
        #     "transport": "stdio",
        # },
    }


# ═══════════════════════════════════════════════════════════════
# Create MCP Agent
# ═══════════════════════════════════════════════════════════════

async def run_mcp_agent(query: str) -> str:
    """Chạy MCP agent với một query.

    Flow:
    1. Kết nối tới MCP Server(s) qua MultiServerMCPClient
    2. Discover tools tự động từ server
    3. Tạo LangGraph ReAct agent với tools discovered
    4. Invoke agent với query
    5. Trả về kết quả

    Args:
        query: Câu hỏi của user.

    Returns:
        Câu trả lời cuối cùng từ agent.
    """
    print(f"\n{'='*60}")
    print(f"🌐 MCP TOOL CALLING")
    print(f"{'='*60}")
    print(f"📝 Query: {query}")
    print(f"{'─'*60}")

    # ── STEP 1: Kết nối tới MCP Server(s) ────────────────────
    print("  📡 Đang kết nối tới MCP Server...")

    mcp_config = get_mcp_config()

    client = MultiServerMCPClient(mcp_config)

    # ── STEP 2: Discover tools từ MCP Server ─────────────
    tools = await client.get_tools()

    print(f"  ✅ Discovered {len(tools)} tools từ MCP Server:")
    for t in tools:
        print(f"     • {t.name}: {t.description[:60]}...")

    print(f"{'─'*60}")

    # ── STEP 3: Tạo LangGraph agent ──────────────────────
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0,
    )

    # create_react_agent tự động tạo StateGraph với:
    # - agent node (LLM)
    # - tool node
    # - conditional edges
    agent = create_react_agent(llm, tools)

    # ── STEP 4: Invoke agent ─────────────────────────────
    result = await agent.ainvoke({"messages": [("human", query)]})

    # In ra các bước trung gian
    for msg in result["messages"]:
        msg_type = msg.__class__.__name__
        if msg_type == "AIMessage" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🤖 LLM quyết định gọi tool: {tc['name']}({tc['args']})")
        elif msg_type == "ToolMessage":
            print(f"  ⚡ MCP Server trả về: {msg.content[:100]}...")

    final_message = result["messages"][-1]

    print(f"\n{'─'*60}")
    print(f"📤 Response: {final_message.content}")
    print(f"{'='*60}\n")

    return final_message.content
