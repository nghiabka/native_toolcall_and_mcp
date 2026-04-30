"""
═══════════════════════════════════════════════════════════════════════
MCP SERVER — Expose tools qua Model Context Protocol
═══════════════════════════════════════════════════════════════════════

Đây là MCP Server — một process/service RIÊNG BIỆT expose tools cho
bất kỳ MCP Client nào kết nối vào.

Điểm khác biệt chính so với Native:
  • Tools KHÔNG nằm trong code agent
  • Tools được expose qua protocol chuẩn (MCP)
  • Bất kỳ agent nào hỗ trợ MCP đều có thể dùng tools này
  • Agent KHÔNG cần biết implementation chi tiết của tools

Kiến trúc:
  ┌───────────────────────────────────────────────────────────┐
  │                      MCP SERVER                          │
  │                                                          │
  │   @mcp.tool()           @mcp.tool()        @mcp.tool()  │
  │   get_weather()         calculate()     search_knowledge()│
  │                                                          │
  │   Transport: stdio (hoặc HTTP/SSE cho production)        │
  └─────────────────────────┬─────────────────────────────────┘
                            │
                     MCP Protocol
                     (JSON-RPC)
                            │
                  ┌─────────▼──────────┐
                  │    MCP CLIENT      │
                  │ (trong Agent app)  │
                  └────────────────────┘

Cách chạy standalone (để test):
    cd /data/learning/agent/native_toolcall_and_mcp
    python -m mcp_tool_calling.mcp_server
"""

import sys
import os

# Đảm bảo import được shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

# Import shared tool functions
from shared.tools import get_weather, calculate, search_knowledge


# ═══════════════════════════════════════════════════════════════
# Khởi tạo MCP Server
# ═══════════════════════════════════════════════════════════════

mcp = FastMCP(
    name="AgentToolServer",
    instructions=(
        "MCP Server cung cấp 3 tools: tra cứu thời tiết, tính toán, "
        "và tìm kiếm knowledge base. Sử dụng cho demo MCP vs Native."
    ),
)


# ═══════════════════════════════════════════════════════════════
# Expose tools qua MCP protocol
# ═══════════════════════════════════════════════════════════════
# Lưu ý: cùng logic với Native, nhưng wrapped bằng @mcp.tool()
# thay vì @tool của LangChain. MCP Client sẽ auto-discover.

@mcp.tool()
def get_weather_mcp(city: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một thành phố.
    Sử dụng khi người dùng hỏi về thời tiết, nhiệt độ, hoặc tình trạng khí hậu.

    Args:
        city: Tên thành phố cần tra cứu (ví dụ: "Hanoi", "Tokyo", "New York")
    """
    return get_weather(city)


@mcp.tool()
def calculate_mcp(expression: str) -> str:
    """Tính toán biểu thức toán học.
    Sử dụng khi người dùng cần tính toán số học, lượng giác, logarit.

    Args:
        expression: Biểu thức toán học (ví dụ: "2 + 3 * 4", "sqrt(16)", "sin(pi/2)")
    """
    return calculate(expression)


@mcp.tool()
def search_knowledge_mcp(query: str) -> str:
    """Tìm kiếm thông tin trong knowledge base nội bộ.
    Sử dụng khi người dùng hỏi về các khái niệm AI, LLM, LangGraph, MCP, RAG, Vector DB.

    Args:
        query: Từ khóa hoặc câu hỏi cần tìm (ví dụ: "LangGraph", "RAG là gì")
    """
    return search_knowledge(query)


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 Starting MCP Server (AgentToolServer)...")
    print("   Transport: stdio")
    print("   Tools: get_weather_mcp, calculate_mcp, search_knowledge_mcp")
    mcp.run(transport="stdio")
