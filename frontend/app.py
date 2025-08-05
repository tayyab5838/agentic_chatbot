import chainlit as cl
import httpx
import json
import asyncio

API_URL = "http://localhost:8000/api/run"

@cl.on_message
async def on_message(user_msg: cl.Message):
    """
    Runs the agent with streaming and only opens Steps for:
      - Agent handoffs (agent_updated_stream_event)
      - Tool calls (tool_call_item)
      - Tool outputs (tool_call_output_item)
    All other LLM-generated tokens are streamed into a regular Chainlit message.
    """
    assistant_msg = cl.Message(content="")

    current_step = None

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", API_URL, json={"user_query": user_msg.content}) as resp:
            async for raw_line in resp.aiter_lines():   
                print("raw line: ", raw_line)
                if not raw_line or not raw_line.startswith(("data: ", "event: ")):
                    continue
                event = json.loads(raw_line.split("data: ")[-1])
                ev_type = event.get("type")
                ev_val = event.get("value", "")

                # ───────── Agent changed:
                if ev_type == "agent_updated":
                    if ev_val != "Triage Agent":

                        # Close any ongoing step
                        if current_step:
                            current_step = None

                        # Show switch step
                        current_step = cl.Step(name=f"🧠 Switched to {ev_val}", type="llm", show_input=False)
                        await current_step.__aenter__()
                        await current_step.stream_token(f"🔄 Agent updated to **{ev_val}**")

                # ───────── Tool call started:
                elif ev_type == "tool_call":
                    print(ev_val)
                    current_step = cl.Step(
                        name=f"🔧  {ev_val['name']}",
                        type="tool",
                        show_input=True
                    )
                    # current_step.input = ev_val['arguments'] # e.g. "add(a=2, b=8)"
                    await current_step.__aenter__()  # Start the step manually
                    current_step.input = ev_val['arguments']
                    await current_step.send()
                    continue

                # ───────── Tool returned:
                elif ev_type == "tool_output":
                    if current_step:
                        await current_step.stream_token(str(ev_val))
                        current_step.output = str(ev_val)
                        await current_step.__aexit__(None, None, None) # type: ignore

                # ───────── Normal LLM token:
                elif ev_type == "token":
                    await assistant_msg.stream_token(ev_val)
                    await asyncio.sleep(0.1)  # delay for displaying smoothly
                

    await assistant_msg.update()
