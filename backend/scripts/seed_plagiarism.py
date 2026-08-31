import asyncio
import sys
import os

# Add backend dir to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from services.plagiarism_guard import seed_known_answers

if __name__ == "__main__":
    asyncio.run(seed_known_answers())
