from typing import List

from pydantic import BaseModel
from typing_extensions import Self

from .._component_config import Component, ComponentModel
from .. import FunctionCall
from ..models import AssistantMessage, ChatCompletionClient, FunctionExecutionResultMessage, LLMMessage
from ..tools import ToolSchema
from ._chat_completion_context import ChatCompletionContext


class TokenLimitedChatCompletionContextConfig(BaseModel):
    model_client: ComponentModel
    token_limit: int | None = None
    tool_schema: List[ToolSchema] | None = None
    initial_messages: List[LLMMessage] | None = None


class TokenLimitedChatCompletionContext(ChatCompletionContext, Component[TokenLimitedChatCompletionContextConfig]):
    """(Experimental) A token based chat completion context maintains a view of the context up to a token limit.

    .. note::

        Added in v0.4.10. This is an experimental component and may change in the future.

    Args:
        model_client (ChatCompletionClient): The model client to use for token counting.
            The model client must implement the :meth:`~autogen_core.models.ChatCompletionClient.count_tokens`
            and :meth:`~autogen_core.models.ChatCompletionClient.remaining_tokens` methods.
        token_limit (int | None): The maximum number of tokens to keep in the context
            using the :meth:`~autogen_core.models.ChatCompletionClient.count_tokens` method.
            If None, the context will be limited by the model client using the
            :meth:`~autogen_core.models.ChatCompletionClient.remaining_tokens` method.
        tools (List[ToolSchema] | None): A list of tool schema to use in the context.
        initial_messages (List[LLMMessage] | None): A list of initial messages to include in the context.

    """

    component_config_schema = TokenLimitedChatCompletionContextConfig
    component_provider_override = "autogen_core.model_context.TokenLimitedChatCompletionContext"

    def __init__(
        self,
        model_client: ChatCompletionClient,
        *,
        token_limit: int | None = None,
        tool_schema: List[ToolSchema] | None = None,
        initial_messages: List[LLMMessage] | None = None,
    ) -> None:
        super().__init__(initial_messages)
        if token_limit is not None and token_limit <= 0:
            raise ValueError("token_limit must be greater than 0.")
        self._token_limit = token_limit
        self._model_client = model_client
        self._tool_schema = tool_schema or []

    async def get_messages(self) -> List[LLMMessage]:
        """Get at most `token_limit` tokens in recent messages. If the token limit is not
        provided, then return as many messages as the remaining token allowed by the model client."""
        messages = list(self._messages)
        if self._token_limit is None:
            remaining_tokens = self._model_client.remaining_tokens(messages, tools=self._tool_schema)
            while remaining_tokens < 0 and len(messages) > 0:
                middle_index = len(messages) // 2
                messages.pop(middle_index)
                remaining_tokens = self._model_client.remaining_tokens(messages, tools=self._tool_schema)
        else:
            token_count = self._model_client.count_tokens(messages, tools=self._tool_schema)
            while token_count > self._token_limit and len(messages) > 0:
                middle_index = len(messages) // 2
                messages.pop(middle_index)
                token_count = self._model_client.count_tokens(messages, tools=self._tool_schema)

        # Remove orphaned FunctionExecutionResultMessages that have no matching
        # AssistantMessage with a corresponding FunctionCall anywhere in the list.
        # This can happen when truncation removes an AssistantMessage from the
        # middle of the list while leaving its paired FunctionExecutionResultMessage.
        messages = self._remove_orphaned_function_results(messages)

        return messages

    def _remove_orphaned_function_results(self, messages: List[LLMMessage]) -> List[LLMMessage]:
        """Remove FunctionExecutionResultMessage instances that have no matching
        FunctionCall in any AssistantMessage within the provided message list."""
        # Collect all call_ids from AssistantMessages
        call_ids: set[str] = set()
        for msg in messages:
            if isinstance(msg, AssistantMessage) and isinstance(msg.content, list):
                for item in msg.content:
                    if isinstance(item, FunctionCall) and item.id:
                        call_ids.add(item.id)

        # Filter out orphaned FunctionExecutionResultMessages
        result: List[LLMMessage] = []
        for msg in messages:
            if isinstance(msg, FunctionExecutionResultMessage):
                # Keep only if at least one result has a matching call_id
                has_match = any(result.call_id in call_ids for result in msg.content if result.call_id)
                if has_match:
                    result.append(msg)
            else:
                result.append(msg)
        return result

    def _to_config(self) -> TokenLimitedChatCompletionContextConfig:
        return TokenLimitedChatCompletionContextConfig(
            model_client=self._model_client.dump_component(),
            token_limit=self._token_limit,
            tool_schema=self._tool_schema,
            initial_messages=self._initial_messages,
        )

    @classmethod
    def _from_config(cls, config: TokenLimitedChatCompletionContextConfig) -> Self:
        return cls(
            model_client=ChatCompletionClient.load_component(config.model_client),
            token_limit=config.token_limit,
            tool_schema=config.tool_schema,
            initial_messages=config.initial_messages,
        )
