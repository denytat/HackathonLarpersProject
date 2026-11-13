import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one short sentence.")
print(r.text)