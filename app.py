# import sys
# from ui.main_window import run_app

# if __name__ == "__main__":
#     # Entry point kept tiny for clarity
#     sys.exit(run_app())

# file: app.py
import sys
from dotenv import load_dotenv

# Load .env before anything else so os.getenv works everywhere
load_dotenv()

from ui.main_window import run_app  # import after load_dotenv

if __name__ == "__main__":
    sys.exit(run_app())
