from agents import AsyncOpenAI, OpenAIChatCompletionsModel # type: ignore
from agents.run import RunConfig
import os 
from dotenv import load_dotenv


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("api key not set")


external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client = external_client
)

run_config = RunConfig(
    model=model,
    model_provider=external_client, # type: ignore
    tracing_disabled=True
)