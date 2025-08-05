# backend/services/agent_runner.py
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, GuardrailFunctionOutput, InputGuardrail, ItemHelpers, function_tool, enable_verbose_stdout_logging # type: ignore
from agents.run import RunConfig
from agents.exceptions import InputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ..helpers.prompt_loader import load_prompt
from ..tools import add, get_weather, get_stock_price
import json
import asyncio
enable_verbose_stdout_logging()

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("api key not set")

triage_prompt = load_prompt("prompts/triage_agent_prompt.md")

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

class ControversialType(BaseModel):
    is_controversial: bool
    reasoning: str


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about a politically controversial question",
    output_type=ControversialType
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly."
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples"
)




async def controversial_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input=input_data, context=ctx.context, run_config=run_config)
    final_output = result.final_output_as(ControversialType)
    print(final_output)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_controversial
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_prompt,
    handoffs=[history_tutor_agent, math_tutor_agent],
    tools=[get_weather, get_stock_price],
    input_guardrails=[
        InputGuardrail(guardrail_function=controversial_guardrail),
    ],
)


async def run_agent_streamed(user_input: str):
    print("user input in runner: ", user_input)
    result = Runner.run_streamed(triage_agent, user_input, run_config=run_config)


    async for event in result.stream_events():
        # Stream tokens from the LLM as they come
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            data = event.data.delta  # type: ignore
            print("event data: ", data)
            yield f"data: {json.dumps({'type': 'token', 'value': data})}\n\n"

        # Handle agent switching events
        elif event.type == "agent_updated_stream_event":
            yield f"data: {json.dumps({'type': 'agent_updated', 'value': event.new_agent.name})}\n\n"

        # Handle run items: tool calls, tool outputs, messages
        elif event.type == "run_item_stream_event":
            item = event.item

            # Tool call start
            if item.type == "tool_call_item":
                print("tool_call_item: ", item.raw_item)
                tool_name = item.raw_item.name  # type: ignore
                tool_input = item.raw_item.arguments  # type: ignore
                print("tool_name:", tool_name)
                print("tool_input:", tool_input)
                yield f"data: {json.dumps({'type': 'tool_call', 'value': item.raw_item.model_dump()})}\n\n"

            # Tool output result
            elif item.type == "tool_call_output_item":
                print("tool output: ", item.output)
                yield f"data: {json.dumps({'type': 'tool_output', 'value': item.output})}\n\n"

            # Message from LLM (buffer until tool calls are handled)
            elif item.type == "message_output_item":
                text = ItemHelpers.text_message_output(item)
                buffered_message = text  # Store message to yield later

        await asyncio.sleep(0)  # Yield control to event loop


    print("=== Run complete ===")
