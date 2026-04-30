"""
Runner cho Native Tool Calling agent.

Cách chạy:
    cd /data/learning/agent/native_toolcall_and_mcp
    python -m native_tool_calling.run
"""

import sys
import os

# Đảm bảo import được shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from native_tool_calling.agent import run_native_agent


def main():
    print("\n" + "█" * 60)
    print("█  DEMO: NATIVE TOOL CALLING với LangGraph              █")
    print("█  Tools được định nghĩa TRỰC TIẾP trong code agent     █")
    print("█" * 60)
    print()
    print("Các tools available:")
    print("  🌤️  weather_tool  — Tra cứu thời tiết")
    print("  🔢  calculator    — Tính toán biểu thức")
    print("  📚  knowledge     — Tìm kiếm knowledge base")
    print()
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

            run_native_agent(query)

        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
