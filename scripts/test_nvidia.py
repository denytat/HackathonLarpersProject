import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url=os.environ["NEMOTRON_BASE_URL"],
    api_key=os.environ["VERDA_INFERENCE_KEY"],
)

resp = client.chat.completions.create(
    model=os.environ["NEMOTRON_MODEL"],
    messages=[{"role": "user",
               "content": "Name the manipulation technique: "
                          "'They don't want you to know the truth, act NOW before it's too late!' "
                          "Reply in JSON with keys technique and explanation."}],
    temperature=0.2,
    max_tokens=4000,
)
choice = resp.choices[0]
print("finish_reason:", choice.finish_reason)
print("content:", choice.message.content)
print("reasoning:", getattr(choice.message, "reasoning_content", None))
print("usage:", resp.usage)