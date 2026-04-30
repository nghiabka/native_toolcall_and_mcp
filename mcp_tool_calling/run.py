"""
Runner cho MCP Tool Calling agent.

Cách chạy:
    cd /data/learning/agent/native_toolcall_and_mcp
    python -m mcp_tool_calling.run
"""

import asyncio
import sys
import os

# Đảm bảo import được shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tool_calling.agent import run_mcp_agent


async def main():
    print("\n" + "█" * 60)
    print("█  DEMO: MCP TOOL CALLING với LangGraph                 █")
    print("█  Tools được expose qua MCP Server riêng biệt          █")
    print("█" * 60)
    print()
    print("Kiến trúc:")
    print("  Agent (MCP Host) ──▶ MCP Client ──▶ MCP Server ──▶ Tools")
    print()
    print("Tools sẽ được DISCOVERED tự động từ MCP Server.")
    print("Gõ 'quit' để thoát.")
    print("─" * 60)

    while True:
        try:
            query = input("\n🧑 Bạn: ").strip()
            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                print("👋 Tạm biệt!")
                break

            await run_mcp_agent(query)

        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
