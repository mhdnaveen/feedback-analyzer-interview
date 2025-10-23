import json
import uuid
import os
import re
from dataclasses import asdict, dataclass
from typing import Optional, Sequence
import logging

from gen_ai_hub.proxy import GenAIHubProxyClient
from gen_ai_hub.proxy.native.openai import OpenAI
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import (
    SAPDataPrivacyIntegration,
    MaskingMethod,
    ProfileEntity,
)



def clean_and_parse_sentiment_response(response: str):
    """
    Cleans and parses the sentiment response from the model.
    
    :param response: The raw string response from the model.
    :return: A dictionary containing the sentiments, or an empty dictionary if parsing fails.
    """
    try:
        # Find the first occurrence of a JSON-like dictionary in the response
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1:
            # Extract the potential JSON substring
            json_string = response[start:end+1]
            # Parse the JSON substring
            return json.loads(json_string)
        else:
            print("No valid dictionary found in the response.")
            return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {}

@dataclass
class ChatMessage:
    """
    Represents a message in a chat conversation.

    Attributes:
        role (str): The role of the message sender (e.g., 'user', 'assistant', 'system').
        content (Optional[str]): The content of the message. Defaults to None.
    """

    content: Optional[str] = None
    masked_data: Optional[str] = None


class OrchestrationClient:
    """
    A client for interacting with the OpenAI API via SAP Orchestration.

    This class provides an interface for using SAP's orchestration service for AI operations,
    including sentiment analysis with data masking and privacy integration.

    Attributes:
        proxy (GenAIHubProxyClient): The proxy client used for making requests.
    """

    def __init__(self):
        self.proxy = GenAIHubProxyClient(
            auth_url=os.getenv("AICORE_AUTH_URL") + "/oauth/token",
            client_id=os.getenv("AICORE_CLIENT_ID"),
            client_secret=os.getenv("AICORE_CLIENT_SECRET"),
            base_url=os.getenv("AICORE_BASE_URL") + "/v2",
            resource_group=os.getenv("AICORE_RESOURCE_GROUP"),
        )
        self.token_usage = None

    def construct_orchestration_config(self, messages: list, model_name: str) -> OrchestrationConfig:
        """
        Creates the orchestration configuration.

        Args:
            gpt_system_prompt (str): The system prompt for GPT.
            feedbacks_prompt (dict): The feedback prompts in a dictionary format.

        Returns:
            OrchestrationConfig: The configuration for orchestration.
        """
        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[
                        ProfileEntity.EMAIL,
                        ProfileEntity.PHONE,
                        ProfileEntity.PERSON,
                        ProfileEntity.LOCATION,
                    ],
                )
            ]
        )

        return OrchestrationConfig(
            template=Template(messages=messages),
            llm=LLM(name=model_name),
            data_masking=data_masking,
        )

    def complete(self, messages: list, model_name: str) -> str:
        """
        Runs the orchestration to perform sentiment analysis on the provided text.

        Args:
            gpt_system_prompt (str): The system prompt for GPT.
            feedbacks_prompt (dict): The feedback prompts in a dictionary format.

        Returns:
            str: The sentiment analysis result in JSON format.
        """
        try:
            config = self.construct_orchestration_config(messages, model_name)
           
            orchestration_service = OrchestrationService(
                api_url=os.getenv("AICORE_API_URL"),
                proxy_client=self.proxy,
                config=config
            )
            completion = orchestration_service.run()
            self.token_usage = completion.orchestration_result.usage
            return ChatMessage(
                content=clean_and_parse_sentiment_response(completion.orchestration_result.choices[0].message.content),
                masked_data=json.loads(
                    json.loads(completion.module_results.input_masking.data['masked_template'])[1]['content']
                )
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return ChatMessage(content=str([]),  masked_data=str([]))
