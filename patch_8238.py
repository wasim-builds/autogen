import glob
import os

files = [
    "python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py",
    "python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py",
    "python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_selector_group_chat.py",
]

old_code = """        for msg in messages:
            if isinstance(msg, HandoffMessage):
                for llm_msg in msg.context:
                    await model_context.add_message(llm_msg)
            await model_context.add_message(msg.to_model_message())"""

new_code = """        from autogen_core.models import SystemMessage, UserMessage
        for msg in messages:
            if isinstance(msg, HandoffMessage):
                for llm_msg in msg.context:
                    if isinstance(llm_msg, SystemMessage):
                        await model_context.add_message(UserMessage(content=llm_msg.content, source=llm_msg.source))
                    else:
                        await model_context.add_message(llm_msg)
            await model_context.add_message(msg.to_model_message())"""

for file in files:
    with open(file, "r") as f:
        content = f.read()
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file, "w") as f:
            f.write(content)
    else:
        print(f"Failed to find old code in {file}")

