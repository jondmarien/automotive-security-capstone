#!/usr/bin/env python3
"""
Test the CLI dashboard logging integration
"""

from datetime import datetime
from pathlib import Path


def test_dashboard_logging():
    """Test the dashboard logging system."""
    print("🔧 Testing CLI Dashboard Logging Integration")
    print("=" * 50)

    # Check if logs directory exists
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ Logs directory doesn't exist yet")
        return False

    # Get current date for expected directory
    current_date = datetime.now().strftime("%Y-%m-%d")
    expected_dir = logs_dir / f"dashboard-{current_date}"

    print(f"📁 Expected log directory: {expected_dir}")

    if expected_dir.exists():
        print("✅ Date-based log directory exists")

        # List log files
        log_files = list(expected_dir.glob("dashboard-*.log"))
        print(f"📄 Found {len(log_files)} log files:")

        for log_file in log_files:
            print(f"   • {log_file.name}")

            # Check file size
            size_kb = log_file.stat().st_size / 1024
            print(f"     Size: {size_kb:.1f} KB")

            # Check if file has content
            if size_kb > 0:
                print("     ✅ File has content")
            else:
                print("     ⚠️  File is empty")
    else:
        print("⚠️  Date-based log directory doesn't exist yet")
        print("   This is normal if the dashboard hasn't been run today")

    print("\\n💡 To test logging with CLI dashboard:")
    print("   1. Run: uv run python cli_dashboard.py --mock")
    print("   2. Use arrow keys, help (?), and quit (q)")
    print(f"   3. Check logs/{current_date}/ for new log files")
    print("   4. Each run creates a new timestamped log file")

    print("\\n📋 Log Structure:")
    print("   logs/")
    print(f"   ├── dashboard-{current_date}/")
    print("   │   ├── dashboard-HH-MM-SS.log")
    print("   │   ├── dashboard-HH-MM-SS.log")
    print("   │   └── dashboard-HH-MM-SS.log")
    print("   └── dashboard-YYYY-MM-DD/")
    print("       └── dashboard-HH-MM-SS.log")

    return True


if __name__ == "__main__":
    test_dashboard_logging()
