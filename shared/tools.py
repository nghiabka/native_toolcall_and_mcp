"""Shared tool definitions — dùng chung cho cả Native và MCP approach.

Mỗi tool là một function đơn giản thực hiện 1 tác vụ cụ thể.
Trong Native approach: các tools này được bind trực tiếp vào LLM.
Trong MCP approach: các tools này được expose qua MCP Server.
"""

import math
import random
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# TOOL 1: Weather — Lấy thông tin thời tiết
# ═══════════════════════════════════════════════════════════════

# Data giả lập thời tiết cho các thành phố
_WEATHER_DATA = {
    "hanoi": {"temp": 32, "condition": "Nắng nóng", "humidity": 75, "wind": "10 km/h"},
    "ho chi minh": {"temp": 35, "condition": "Nắng gắt", "humidity": 80, "wind": "8 km/h"},
    "da nang": {"temp": 29, "condition": "Mây rải rác", "humidity": 70, "wind": "15 km/h"},
    "tokyo": {"temp": 22, "condition": "Trời quang", "humidity": 55, "wind": "12 km/h"},
    "new york": {"temp": 18, "condition": "Có mưa nhẹ", "humidity": 65, "wind": "20 km/h"},
    "london": {"temp": 14, "condition": "Nhiều mây", "humidity": 80, "wind": "25 km/h"},
    "paris": {"temp": 20, "condition": "Nắng đẹp", "humidity": 50, "wind": "10 km/h"},
    "singapore": {"temp": 31, "condition": "Nóng ẩm", "humidity": 85, "wind": "5 km/h"},
}


def get_weather(city: str) -> str:
    """Lấy thông tin thời tiết hiện tại của một thành phố.

    Args:
        city: Tên thành phố cần tra cứu thời tiết (ví dụ: "Hanoi", "Tokyo").

    Returns:
        Chuỗi mô tả thời tiết hiện tại của thành phố.
    """
    city_lower = city.lower().strip()
    data = _WEATHER_DATA.get(city_lower)

    if data:
        return (
            f"🌤️ Thời tiết tại {city}:\n"
            f"  • Nhiệt độ: {data['temp']}°C\n"
            f"  • Tình trạng: {data['condition']}\n"
            f"  • Độ ẩm: {data['humidity']}%\n"
            f"  • Gió: {data['wind']}\n"
            f"  • Cập nhật lúc: {datetime.now().strftime('%H:%M %d/%m/%Y')}"
        )
    else:
        # Sinh data ngẫu nhiên cho thành phố không có trong danh sách
        temp = random.randint(10, 38)
        conditions = ["Nắng", "Nhiều mây", "Mưa nhẹ", "Trời quang", "Sương mù"]
        return (
            f"🌤️ Thời tiết tại {city}:\n"
            f"  • Nhiệt độ: {temp}°C\n"
            f"  • Tình trạng: {random.choice(conditions)}\n"
            f"  • Độ ẩm: {random.randint(40, 90)}%\n"
            f"  • Gió: {random.randint(5, 30)} km/h\n"
            f"  • Cập nhật lúc: {datetime.now().strftime('%H:%M %d/%m/%Y')}"
        )


# ═══════════════════════════════════════════════════════════════
# TOOL 2: Calculator — Tính toán biểu thức toán học
# ═══════════════════════════════════════════════════════════════

def calculate(expression: str) -> str:
    """Tính toán một biểu thức toán học.

    Hỗ trợ: +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e.

    Args:
        expression: Biểu thức toán học cần tính (ví dụ: "2 + 3 * 4", "sqrt(16)", "sin(pi/2)").

    Returns:
        Kết quả tính toán dưới dạng chuỗi.
    """
    # Các hàm toán học an toàn được phép sử dụng
    safe_dict = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"🔢 Kết quả: {expression} = {result}"
    except Exception as e:
        return f"❌ Lỗi khi tính: {expression} → {str(e)}"


# ═══════════════════════════════════════════════════════════════
# TOOL 3: Knowledge Search — Tìm kiếm trong knowledge base
# ═══════════════════════════════════════════════════════════════

# Knowledge base giả lập
_KNOWLEDGE_BASE = [
    {
        "topic": "LangGraph",
        "content": (
            "LangGraph là framework của LangChain để xây dựng agentic applications. "
            "Nó sử dụng khái niệm graph (đồ thị) với nodes và edges để định nghĩa "
            "luồng xử lý của agent. Hỗ trợ StateGraph, cycles, checkpointing, "
            "và human-in-the-loop patterns."
        ),
    },
    {
        "topic": "MCP",
        "content": (
            "Model Context Protocol (MCP) là giao thức chuẩn do Anthropic phát triển "
            "để kết nối LLM với các nguồn dữ liệu và tools bên ngoài. Kiến trúc gồm "
            "MCP Host, MCP Client, và MCP Server. Hỗ trợ transport qua stdio và HTTP/SSE."
        ),
    },
    {
        "topic": "Function Calling",
        "content": (
            "Function Calling (hay Tool Calling) cho phép LLM gọi các hàm được định nghĩa "
            "trước. LLM phân tích câu hỏi, quyết định tool nào cần gọi và với tham số gì. "
            "Kết quả trả về được LLM tổng hợp thành câu trả lời cuối cùng."
        ),
    },
    {
        "topic": "RAG",
        "content": (
            "Retrieval-Augmented Generation (RAG) là kỹ thuật kết hợp tìm kiếm thông tin "
            "(Retrieval) với sinh văn bản (Generation). Dữ liệu được vector hóa và lưu "
            "trong Vector DB. Khi có câu hỏi, hệ thống tìm chunks liên quan rồi đưa "
            "vào context để LLM trả lời chính xác hơn."
        ),
    },
    {
        "topic": "Vector Database",
        "content": (
            "Vector Database (VectorDB) là cơ sở dữ liệu chuyên lưu trữ và tìm kiếm "
            "vector embeddings. Các VectorDB phổ biến: Qdrant, Pinecone, Weaviate, Chroma. "
            "Hỗ trợ tìm kiếm theo độ tương đồng (similarity search) với cosine, dot product."
        ),
    },
    {
        "topic": "AI Agent",
        "content": (
            "AI Agent là hệ thống AI tự chủ có khả năng: nhận nhiệm vụ, lập kế hoạch, "
            "sử dụng tools, và đưa ra quyết định. Các thành phần chính: LLM (bộ não), "
            "Memory (bộ nhớ), Tools (công cụ), và Planning (lập kế hoạch). "
            "Framework phổ biến: LangGraph, CrewAI, AutoGen."
        ),
    },
]


def search_knowledge(query: str) -> str:
    """Tìm kiếm thông tin trong knowledge base nội bộ.

    Tìm kiếm theo từ khóa trong các bài viết về AI, LLM, và các công nghệ liên quan.

    Args:
        query: Từ khóa hoặc câu hỏi cần tìm (ví dụ: "LangGraph là gì", "RAG hoạt động thế nào").

    Returns:
        Thông tin tìm được từ knowledge base, hoặc thông báo không tìm thấy.
    """
    query_lower = query.lower()
    results = []

    for item in _KNOWLEDGE_BASE:
        # Tìm kiếm đơn giản theo keyword matching
        if (
            query_lower in item["topic"].lower()
            or any(word in item["content"].lower() for word in query_lower.split() if len(word) > 2)
        ):
            results.append(item)

    if results:
        output = f"📚 Tìm thấy {len(results)} kết quả cho '{query}':\n\n"
        for i, item in enumerate(results, 1):
            output += f"  [{i}] {item['topic']}:\n"
            output += f"      {item['content']}\n\n"
        return output.strip()
    else:
        return f"📚 Không tìm thấy thông tin về '{query}' trong knowledge base."
