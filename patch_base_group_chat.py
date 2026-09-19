with open("python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py", "r") as f:
    content = f.read()

old_code = """        self._name = name
        self._description = description
        if len(participants) == 0:
            raise ValueError("At least one participant is required.")
        if len(participants) != len(set(participant.name for participant in participants)):
            raise ValueError("The participant names must be unique.")"""

new_code = """        self._name = name
        self._description = description
        if not participants or not isinstance(participants, list):
            raise ValueError("Participants must be a non-empty list of ChatAgent or Team instances.")
        for participant in participants:
            if not isinstance(participant, (ChatAgent, Team)):
                raise ValueError("Each participant must be a ChatAgent or Team instance.")
        if len(participants) == 0:
            raise ValueError("At least one participant is required.")
        if len(participants) != len(set(participant.name for participant in participants)):
            raise ValueError("The participant names must be unique.")"""

content = content.replace(old_code, new_code)

with open("python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py", "w") as f:
    f.write(content)
