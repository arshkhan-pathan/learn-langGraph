from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
# llm = ChatOpenAI(model="gpt-4o-mini")
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
)