#!/usr/bin/env python3
"""
Debug script to test the Cover Agent workflow step by step
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.cover_agent import CoverAgent

def main():
    print("🔧 DEBUG: Starting Cover Agent debug session...")
    
    # Create CoverAgent instance
    try:
        agent = CoverAgent(
            source_file_path="test_calculator.py",
            test_file_path="test_test_calculator.py", 
            code_coverage_report_path="coverage.xml",
            test_command="python -m pytest test_test_calculator.py -v",
            desired_coverage=90,
            max_iterations=1  # Just one iteration for debugging
        )
        print("✅ DEBUG: CoverAgent created successfully")        # Skip Ollama availability check for now
        print("⏭️  DEBUG: Skipping Ollama check for debugging...")
        ollama_available = False
          # Skip Ollama check and run in demo mode directly
        print("🎭 DEBUG: Running in demo mode (forced)...")
        result = agent._run_demo_mode()
        print(f"✅ DEBUG: Demo mode result: {result}")
        
    except Exception as e:
        print(f"❌ DEBUG: Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
