
from agents import Agent
from pydantic import BaseModel

class ControversialType(BaseModel):
    is_controversial: bool
    reasoning: str


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about a politically controversial question",
    output_type=ControversialType
)