# -*- coding: utf-8 -*-
# The above line explicitly declares the file's encoding as UTF-8.

from openai import OpenAI, OpenAIError
from config import Config
import json
import logging
import httpx # <--- NEW IMPORT: Required for creating a custom HTTP client
import os    # Keep os import, might be useful for environment checks

# Configure basic logging to show messages in the terminal where Flask runs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to clean strings ---
def sanitize_text(text: str) -> str:
    """
    Aggressively removes common Unicode line/paragraph separator characters
    that can cause UnicodeEncodeError with ASCII codecs.
    Also ensures the text is a string before processing.
    """
    if not isinstance(text, str):
        text = str(text) # Ensure it's a string before processing
    return text.replace('\u2028', '').replace('\u2029', '')

class NLUService:
    def __init__(self):
        # --- NEW: Create a custom httpx client for explicit encoding control ---
        # This client will be used by the OpenAI library.
        # While httpx typically handles UTF-8, explicitly configuring it can
        # help with stubborn encoding issues, especially if invisible chars persist.
        self.http_client = httpx.Client(
            # You can add transport/proxy/timeout settings here if needed later
            # transport=httpx.HTTPTransport(retries=3),
            # timeout=30.0,
        )

        # --- MODIFIED: Pass the custom http_client to the OpenAI client ---
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            http_client=self.http_client # Pass our custom httpx client
        )
        # ------------------------------------------------------------------

        logging.info(f"NLUService initialized. OpenAI API Key (first 5 chars): {Config.OPENAI_API_KEY[:5] if Config.OPENAI_API_KEY else 'N/A'}")
        if not Config.OPENAI_API_KEY:
            logging.error("CRITICAL ERROR: OPENAI_API_KEY is not set in config.py. Please check .env file.")

        # Manually re-typed and sanitized original system message content
        # --- CRITICAL: Manually RE-TYPE this string or paste from a plain source ---
        original_system_content = (
            "You are an expert PC building AI assistant. "
            "Your goal is to understand user requirements (budget, use case, aesthetic preferences, desired peripherals like monitor/keyboard/mouse) "
            "and then recommend a complete PC build. "
            "Ask clarifying questions one by one. "
            "When you have enough information, output a JSON object with the extracted parameters. "
            "Be friendly, helpful, and concise. "
            "Possible use_cases: 'gaming', 'productivity', 'streaming', 'general'. "
            "Possible aesthetic_tags: 'RGB', 'minimalist', 'white', 'black'. "
            "If the user asks for a recommendation, provide it only after extracting all necessary information."
            "When responding with a recommendation, present it in a human-readable format, then state the collected parameters as a JSON."
        )

        self.system_message = {
            "role": "system",
            "content": sanitize_text(original_system_content) # Sanitize here once at init
        }
        logging.debug(f"System message sanitized and loaded: {self.system_message['content']}")


    def get_chat_response(self, user_message: str, conversation_history: list = None):
        if conversation_history is None:
            conversation_history = [self.system_message]
        else:
            # Ensure system message is always first if starting a new conversation
            if not conversation_history or conversation_history[0]["role"] != "system":
                conversation_history.insert(0, self.system_message)

        # Sanitize the incoming user message before adding it to history
        user_message_sanitized = sanitize_text(user_message)
        conversation_history.append({"role": "user", "content": user_message_sanitized})

        logging.info(f"Attempting to get chat response for user message: '{user_message_sanitized}'")
        logging.debug(f"Conversation history sent to OpenAI: {conversation_history}")

        try:
            # The conversation_history list should now only contain already-sanitized strings
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history, # Use the list with pre-sanitized content
                max_tokens=500,
                temperature=0.7,
            )

            # Access the content correctly: response.choices is a list
            ai_response_content = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": ai_response_content})
            logging.info(f"OpenAI chat response received (first 100 chars): '{ai_response_content[:100]}'...")
            return ai_response_content, conversation_history

        except OpenAIError as e: # Catch specific OpenAI API errors
            logging.error(f"OpenAI API Error in get_chat_response: {e}")
            return "I'm sorry, I encountered an issue with the AI service. Please check your API key and network connection.", conversation_history
        except Exception as e:
            logging.error(f"General Error in get_chat_response: {e}", exc_info=True) # Log full traceback
            return "I'm sorry, I'm having trouble understanding right now. Can you please try again?", conversation_history

    def extract_parameters(self, user_input: str, conversation_history: list = None) -> dict:
        # Sanitize the incoming user_input for parameter extraction
        user_input_sanitized = sanitize_text(user_input)

        # Manually re-typed and sanitized system message for parameter extraction
        system_prompt_for_extraction = sanitize_text("You are a helpful assistant that extracts information from text into JSON format. Always respond with a valid JSON object, even if empty. If no parameters are found, output an empty JSON object {}.")

        # Manually re-typed and sanitized user prompt for parameter extraction
        user_prompt_for_extraction = sanitize_text(
            f"Given the following user input and conversation history, extract the following parameters as a JSON object: "
            f"budget (float), use_case (string, e.g., 'gaming', 'productivity'), "
            f"aesthetic (string, e.g., 'RGB', 'minimalist'), monitor (boolean), keyboard (boolean), mouse (boolean), "
            f"and any other specific part requests (e.g., 'cpu_brand', 'gpu_brand'). "
            f"If a parameter is not mentioned or clearly implied, omit it. "
            f"Only output the JSON object. If no parameters are found, output an empty JSON object {{}}."
            f"\n\nConversation History: {json.dumps(conversation_history[-3:] if conversation_history else [])}"
            f"\nUser Input: {user_input_sanitized}" # Use the sanitized user_input
        )

        prompt_messages = [
            {"role": "system", "content": system_prompt_for_extraction},
            {"role": "user", "content": user_prompt_for_extraction}
        ]

        logging.info(f"Attempting to extract parameters for user input: '{user_input_sanitized}'")
        logging.debug(f"Prompt sent for extraction: {prompt_messages[-1]['content']}")

        try:
            # The prompt_messages list should now only contain already-sanitized strings
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=prompt_messages, # Use the list with pre-sanitized content
                max_tokens=200,
                temperature=0.0
            )

            json_str = response.choices[0].message.content.strip()
            logging.info(f"Raw GPT extraction response (first 100 chars): '{json_str[:100]}'...")

            # Clean up potential markdown code block
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json\n", "").replace("\n```", "")

            parameters = json.loads(json_str)
            logging.info(f"Successfully extracted parameters: {parameters}")
            return parameters
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error in extract_parameters: {e}\nRaw GPT response was: '{json_str}'", exc_info=True)
            return {}
        except OpenAIError as e:
            logging.error(f"OpenAI API Error in extract_parameters: {e}")
            return {}
        except Exception as e:
            logging.error(f"General Error in extract_parameters: {e}", exc_info=True)
            return {}