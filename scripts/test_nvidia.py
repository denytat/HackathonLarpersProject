
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)

model = os.environ["NVIDIA_MODEL"]
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user",
               "content": "Name the manipulation technique: "
                          "'They don't want you to know the truth, act NOW before it's too late!' "
                          "Reply in JSON with keys technique and explanation."}],
    temperature=0.2,
    max_tokens=300,
)
print(resp.choices[0].message.content)