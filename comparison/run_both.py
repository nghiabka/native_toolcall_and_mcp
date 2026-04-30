"""
═══════════════════════════════════════════════════════════════════════
COMPARISON — Chạy cả 2 approach side-by-side
═══════════════════════════════════════════════════════════════════════

Script này chạy cùng 1 query trên cả Native và MCP approach,
cho phép so sánh trực tiếp:
  - Kết quả có giống nhau không?
  - Flow xử lý khác nhau thế nào?
  - Thời gian response?

Cách chạy:
    cd /data/learning/agent/native_toolcall_and_mcp
    python -m comparison.run_both
"""

import asyncio
import sys
import os
import time

# Đảm bảo import được shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from native_tool_calling.agent import run_native_agent
from mcp_tool_calling.agent import run_mcp_agent


# Các câu hỏi test demo
DEMO_QUERIES = [
    "Thời tiết ở Hà Nội hôm nay thế nào?",
    "Tính cho tôi: (15 + 25) * 3 - sqrt(144)",
    "LangGraph là gì? So sánh với MCP?",
]


async def run_comparison(query: str):
    """Chạy cùng 1 query trên cả 2 approach và so sánh."""

    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "  🔄 SO SÁNH: NATIVE vs MCP TOOL CALLING".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print("║" + f"  Query: {query[:50]}".ljust(58) + "║")
    print("╚" + "═" * 58 + "╝")

    # ── Run Native Approach ───────────────────────────────────
    print("\n▼ ▼ ▼  APPROACH 1: NATIVE  ▼ ▼ ▼")
    start_native = time.time()
    try:
        native_result = run_native_agent(query)
    except Exception as e:
        native_result = f"❌ Error: {e}"
    time_native = time.time() - start_native

    # ── Run MCP Approach ──────────────────────────────────────
    print("\n▼ ▼ ▼  APPROACH 2: MCP  ▼ ▼ ▼")
    start_mcp = time.time()
    try:
        mcp_result = await run_mcp_agent(query)
    except Exception as e:
        mcp_result = f"❌ Error: {e}"
    time_mcp = time.time() - start_mcp

    # ── Summary ───────────────────────────────────────────────
    print("\n")
    print("┌" + "─" * 58 + "┐")
    print("│" + "  📊 KẾT QUẢ SO SÁNH".center(58) + "│")
    print("├" + "─" * 58 + "┤")
    print("│" + f"  ⏱️  Native: {time_native:.2f}s".ljust(58) + "│")
    print("│" + f"  ⏱️  MCP:    {time_mcp:.2f}s".ljust(58) + "│")
    print("│" + f"  📈 Chênh lệch: {abs(time_mcp - time_native):.2f}s".ljust(58) + "│")
    print("├" + "─" * 58 + "┤")

    if time_native < time_mcp:
        print("│" + "  🏆 Native NHANH hơn (ít overhead hơn)".ljust(58) + "│")
    else:
        print("│" + "  🏆 MCP NHANH hơn".ljust(58) + "│")

    print("│" + "".ljust(58) + "│")
    print("│" + "  💡 Lưu ý: MCP chậm hơn do phải:".ljust(58) + "│")
    print("│" + "     • Khởi động MCP Server subprocess".ljust(58) + "│")
    print("│" + "     • Discover tools qua protocol".ljust(58) + "│")
    print("│" + "     • Giao tiếp qua JSON-RPC".ljust(58) + "│")
    print("│" + "     Nhưng lợi ích: modularity, reusability!".ljust(58) + "│")
    print("└" + "─" * 58 + "┘")

    return native_result, mcp_result


async def main():
    print("\n" + "█" * 60)
    print("█  COMPARISON: NATIVE vs MCP TOOL CALLING               █")
    print("█  Chạy cùng query trên cả 2 approach                   █")
    print("█" * 60)
    print()
    print("Chọn mode:")
    print("  [1] Chạy demo queries tự động")
    print("  [2] Nhập query thủ công")
    print()

    choice = input("Chọn (1/2): ").strip()

    if choice == "1":
        print(f"\n🚀 Chạy {len(DEMO_QUERIES)} demo queries...\n")
        for i, query in enumerate(DEMO_QUERIES, 1):
            print(f"\n{'#'*60}")
            print(f"  DEMO {i}/{len(DEMO_QUERIES)}")
            print(f"{'#'*60}")
            await run_comparison(query)
            if i < len(DEMO_QUERIES):
                input("\n⏎  Nhấn Enter để tiếp tục...")
    else:
        while True:
            try:
                query = input("\n🧑 Nhập query (hoặc 'quit'): ").strip()
                if not query:
                    continue
                if query.lower() in ("quit", "exit", "q"):
                    break
                await run_comparison(query)
            except KeyboardInterrupt:
                break

    print("\n👋 Hoàn tất so sánh!")


if __name__ == "__main__":
    asyncio.run(main())
