import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print("GOOGLE_API_KEY prefix:", repr(api_key[:6] if api_key else None))
print("cwd:", os.getcwd())
print(".env exists:", os.path.exists(".env"))

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
    max_output_tokens=2048,
)

response = llm.invoke("Summarize this resume in 3 bullet points for an AI Engineer role in Ireland: [paste a short version of your resume summary here]")

print("\nLLM RESPONSE:\n")
print(response.content)

