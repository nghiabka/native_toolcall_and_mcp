# 🔧 Native Tool Calling vs 🌐 MCP Tool Calling — Demo với LangGraph

Project demo minh họa **2 cách tiếp cận Tool Calling** trong Agentic AI, sử dụng **LangGraph** + **Google Gemini**.

---

## 📖 Giải thích Concept

### Tool Calling là gì?

Tool Calling (hay Function Calling) cho phép LLM **gọi các hàm bên ngoài** để lấy dữ liệu hoặc thực hiện hành động. Thay vì trả lời bằng kiến thức sẵn có, LLM sẽ:

1. Phân tích câu hỏi → quyết định cần tool nào
2. Sinh ra lời gọi tool (tên function + arguments)
3. Agent thực thi tool → lấy kết quả
4. LLM tổng hợp kết quả → trả lời user

### 2 cách tiếp cận

```
┌─────────────────────────────────────────────────────────────────┐
│                    NATIVE TOOL CALLING                         │
│                                                                │
│  User ──▶ Agent ──▶ LLM ──▶ Tool (trực tiếp) ──▶ Response    │
│                                                                │
│  • Tools nằm TRONG code agent                                 │
│  • Import trực tiếp, gọi trực tiếp                            │
│  • Đơn giản, nhanh, ít overhead                               │
│  • Nhưng: tight coupling, khó share giữa agents               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      MCP TOOL CALLING                          │
│                                                                │
│  User ──▶ Agent ──▶ MCP Client ──▶ MCP Server ──▶ Tool        │
│                (Host)          (Protocol)      (Remote)        │
│                                                                │
│  • Tools nằm NGOÀI agent, trên MCP Server riêng               │
│  • Agent discover tools DYNAMIC qua protocol                   │
│  • Chuẩn hóa, share được, multi-agent                          │
│  • Nhưng: phức tạp hơn, thêm latency                          │
└─────────────────────────────────────────────────────────────────┘
```

### Khi nào dùng gì?

| Tiêu chí | Native | MCP |
|---|---|---|
| **Dự án nhỏ, ít tools** | ✅ Phù hợp | ❌ Overkill |
| **Nhiều agents cùng dùng tools** | ❌ Copy-paste | ✅ Share MCP Server |
| **Tools của bên thứ 3** | ❌ Tự implement | ✅ Dùng MCP Server có sẵn |
| **Cần thêm/bớt tools runtime** | ❌ Phải deploy lại | ✅ Chỉ sửa MCP Server |
| **Performance critical** | ✅ Nhanh hơn | ❌ Thêm overhead protocol |
| **Microservices architecture** | ❌ Monolithic | ✅ Tách biệt |

---

## 📁 Cấu trúc Project

```
native_toolcall_and_mcp/
├── shared/                      # Tools & config dùng chung
│   ├── tools.py                 # 3 tool functions (weather, calc, search)
│   └── config.py                # Google API Key config
│
├── native_tool_calling/         # Approach 1: Native
│   ├── agent.py                 # LangGraph StateGraph + bind_tools
│   └── run.py                   # Interactive demo
│
├── mcp_tool_calling/            # Approach 2: MCP
│   ├── mcp_server.py            # FastMCP Server expose tools
│   ├── agent.py                 # MCP Client + LangGraph ReAct agent
│   └── run.py                   # Interactive demo
│
├── comparison/                  # So sánh side-by-side
│   └── run_both.py              # Chạy cùng query trên cả 2
│
├── pyproject.toml               # uv project config + dependencies
├── uv.lock                      # Lock file (auto-generated)
├── .env.example
└── README.md                    # ← Bạn đang đọc file này
```

---

## 🚀 Setup & Chạy

### 1. Install dependencies (dùng `uv`)

```bash
cd /data/learning/agent/native_toolcall_and_mcp

# Nếu chưa có uv:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (uv tự tạo venv + install)
uv sync
```

### 2. Cấu hình API Key

```bash
cp .env.example .env
# Sửa .env, thay GOOGLE_API_KEY bằng key thật từ Google AI Studio
```

### 3. Chạy Demo

```bash
# ── Native Tool Calling ──────────────────────────────
uv run python -m native_tool_calling.run

# ── MCP Tool Calling ─────────────────────────────────
uv run python -m mcp_tool_calling.run

# ── So sánh Side-by-Side ─────────────────────────────
uv run python -m comparison.run_both
```

---

## 🧪 Demo Queries gợi ý

```
Thời tiết ở Hà Nội hôm nay thế nào?
Tính (15 + 25) * 3 - sqrt(144)
LangGraph là gì?
Tìm thông tin về RAG và Vector Database
Thời tiết Tokyo và tính 100 / 7
```

---

## 🔍 Deep Dive: Code Comparison

### Native: Agent bind tools trực tiếp

```python
# native_tool_calling/agent.py

# 1. Wrap functions thành LangChain Tools
@tool
def weather_tool(city: str) -> str:
    """Lấy thời tiết..."""
    return get_weather(city)

# 2. Bind vào LLM
llm_with_tools = llm.bind_tools([weather_tool, ...])

# 3. Build graph
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.add_conditional_edges("agent", tools_condition)
```

### MCP: Agent discover tools từ server

```python
# mcp_tool_calling/agent.py

# 1. Kết nối MCP Server
async with MultiServerMCPClient(config) as client:
    # 2. Discover tools TỰ ĐỘNG
    tools = client.get_tools()

    # 3. Tạo agent (tools đến từ bên ngoài!)
    agent = create_react_agent(llm, tools)
```

### MCP Server: Expose tools qua protocol

```python
# mcp_tool_calling/mcp_server.py

mcp = FastMCP("AgentToolServer")

@mcp.tool()
def get_weather_mcp(city: str) -> str:
    """..."""
    return get_weather(city)

mcp.run(transport="stdio")
```

---

## 💡 Key Takeaways

1. **Cùng logic, khác cách expose** — Cả 2 approach dùng cùng tool functions, chỉ khác cách agent truy cập chúng.

2. **Native = đơn giản + hiệu quả** — Phù hợp khi bạn kiểm soát toàn bộ code và không cần share tools.

3. **MCP = chuẩn hóa + mở rộng** — Phù hợp khi cần ecosystem tools lớn, multi-agent, hoặc tích hợp bên thứ 3.

4. **Không phải chọn 1** — Trong thực tế, có thể dùng hybrid: tools core thì native, tools bên ngoài thì MCP.
