"""
═══════════════════════════════════════════════════════════════════════
NATIVE TOOL CALLING — Agent với tools được định nghĩa trực tiếp
═══════════════════════════════════════════════════════════════════════

Approach này:
  1. Tools được import trực tiếp vào code agent (procedural memory)
  2. Tools được wrap bằng @tool decorator → LangChain Tool objects
  3. Bind tools vào LLM bằng .bind_tools()
  4. LangGraph StateGraph quản lý flow: Agent → Tool → Agent → ...

Flow:
  ┌─────────┐     ┌───────────┐     ┌───────────┐
  │  User   │────▶│   Agent   │────▶│  LLM +    │
  │  Query  │     │  (Node)   │     │  Tools    │
  └─────────┘     └─────┬─────┘     └─────┬─────┘
                        │                  │
                        │    tool_call     │
                        │◀─────────────────┘
                        │
                  ┌─────▼─────┐
                  │   Tool    │    ← Gọi function TRỰC TIẾP
                  │   Node    │
                  └─────┬─────┘
                        │
                        │   tool_result
                        ▼
                  ┌───────────┐
                  │   Agent   │────▶ Final Response
                  │  (Node)   │
                  └───────────┘
"""

from typing import Annotated, TypedDict

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Import shared tools (functions thuần)
from shared.tools import get_weather, calculate, search_knowledge
from shared.config import GOOGLE_API_KEY, GOOGLE_MODEL_NAME


# ═══════════════════════════════════════════════════════════════
# STEP 1: Wrap shared functions thành LangChain Tools
# ═══════════════════════════════════════════════════════════════
# Trong Native approach, ta wrap functions bằng @tool decorator
# để LLM biết được signature và description của mỗi tool.

@tool
def weather_tool(city: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một thành phố.
    Sử dụng khi người dùng hỏi về thời tiết, nhiệt độ, hoặc tình trạng khí hậu.

    Args:
        city: Tên thành phố cần tra cứu (ví dụ: "Hanoi", "Tokyo", "New York")
    """
    return get_weather(city)


@tool
def calculator_tool(expression: str) -> str:
    """Tính toán biểu thức toán học.
    Sử dụng khi người dùng cần tính toán số học, lượng giác, logarit.

    Args:
        expression: Biểu thức toán học (ví dụ: "2 + 3 * 4", "sqrt(16)", "sin(pi/2)")
    """
    return calculate(expression)


@tool
def knowledge_tool(query: str) -> str:
    """Tìm kiếm thông tin trong knowledge base nội bộ.
    Sử dụng khi người dùng hỏi về các khái niệm AI, LLM, LangGraph, MCP, RAG, Vector DB.

    Args:
        query: Từ khóa hoặc câu hỏi cần tìm (ví dụ: "LangGraph", "RAG là gì")
    """
    return search_knowledge(query)


# Danh sách tất cả tools
ALL_TOOLS = [weather_tool, calculator_tool, knowledge_tool]


# ═══════════════════════════════════════════════════════════════
# STEP 2: Định nghĩa State cho graph
# ═══════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """State của agent — chứa lịch sử messages."""
    messages: Annotated[list, add_messages]


# ═══════════════════════════════════════════════════════════════
# STEP 3: Build LangGraph StateGraph
# ═══════════════════════════════════════════════════════════════

def create_native_agent():
    """Tạo LangGraph agent với Native Tool Calling.

    Returns:
        Compiled LangGraph graph sẵn sàng invoke.
    """
    # ── Khởi tạo LLM với tools ───────────────────────────────
    llm = ChatGoogleGenerativeAI(
        model=GOOGLE_MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )

    # Bind tools vào LLM — đây là bước quan trọng nhất!
    # LLM sẽ biết được có những tools nào available
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # ── Định nghĩa các Nodes ─────────────────────────────────

    def agent_node(state: AgentState):
        """Node chính: gọi LLM để quyết định action tiếp theo.

        LLM sẽ:
        - Trả lời trực tiếp nếu không cần tool
        - Hoặc trả về tool_call nếu cần gọi tool
        """
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # ToolNode tự động thực thi tool_calls từ LLM response
    tool_node = ToolNode(ALL_TOOLS)

    # ── Build Graph ───────────────────────────────────────────
    graph_builder = StateGraph(AgentState)

    # Thêm nodes
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", tool_node)

    # Thêm edges
    graph_builder.add_edge(START, "agent")

    # Conditional edge: agent → tools (nếu có tool_call) hoặc → END
    graph_builder.add_conditional_edges("agent", tools_condition)

    # Sau khi tool thực thi xong → quay lại agent để tổng hợp
    graph_builder.add_edge("tools", "agent")

    # Compile graph
    graph = graph_builder.compile()

    return graph


def run_native_agent(query: str) -> str:
    """Chạy Native agent với một query.

    Args:
        query: Câu hỏi của user.

    Returns:
        Câu trả lời cuối cùng từ agent.
    """
    graph = create_native_agent()

    print(f"\n{'='*60}")
    print(f"🔧 NATIVE TOOL CALLING")
    print(f"{'='*60}")
    print(f"📝 Query: {query}")
    print(f"{'─'*60}")

    result = graph.invoke({"messages": [("human", query)]})

    # Lấy message cuối cùng (response)
    final_message = result["messages"][-1]

    # In ra các bước trung gian
    for msg in result["messages"]:
        msg_type = msg.__class__.__name__
        if msg_type == "HumanMessage":
            pass  # Đã in ở trên
        elif msg_type == "AIMessage" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🤖 LLM quyết định gọi tool: {tc['name']}({tc['args']})")
        elif msg_type == "ToolMessage":
            print(f"  ⚡ Tool trả về: {msg.content[:100]}...")
        elif msg_type == "AIMessage":
            print(f"\n  💬 Câu trả lời:")

    print(f"\n{'─'*60}")
    print(f"📤 Response: {final_message.content}")
    print(f"{'='*60}\n")

    return final_message.content
