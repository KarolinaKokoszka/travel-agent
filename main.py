import travel_agent
import gui
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    travel_agent.configure_api(gemini_api_key)
    gui.main()

if __name__ == "__main__":
    main()
