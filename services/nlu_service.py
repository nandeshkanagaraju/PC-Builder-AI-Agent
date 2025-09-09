from openai import OpenAI
from config import Config
import json

class NLUService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        # System message to define the AI's persona and task
        self.system_message = {
            "role": "system",
            "content": (
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
        }

    def get_chat_response(self, user_message: str, conversation_history: list = None):
        if conversation_history is None:
            conversation_history = [self.system_message]
        else:
            # Ensure system message is always first if starting a new conversation, or prepend if necessary
            if not conversation_history or conversation_history[0]["role"] != "system":
                conversation_history.insert(0, self.system_message)


        conversation_history.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can use "gpt-4" for better quality, but higher cost
                messages=conversation_history,
                max_tokens=500,
                temperature=0.7,
                # Add a stop sequence if you want to control the output format, e.g., to ensure JSON
                # stop=["```json"]
            )
            ai_response_content = response.choices.message.content
            conversation_history.append({"role": "assistant", "content": ai_response_content})
            return ai_response_content, conversation_history

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "I'm sorry, I'm having trouble understanding right now. Can you please try again?", conversation_history

    def extract_parameters(self, user_input: str, conversation_history: list = None) -> dict:
        # Use GPT's function calling or a specific prompt to extract structured data
        prompt = (
            f"Given the following user input and conversation history, extract the following parameters as a JSON object: "
            f"budget (float), use_case (string, e.g., 'gaming', 'productivity'), "
            f"aesthetic (string, e.g., 'RGB', 'minimalist'), monitor (boolean), keyboard (boolean), mouse (boolean), "
            f"and any other specific part requests (e.g., 'cpu_brand', 'gpu_brand'). "
            f"If a parameter is not mentioned or clearly implied, omit it. "
            f"Only output the JSON object."
            f"\n\nConversation History: {json.dumps(conversation_history[-3:])}" # Last 3 turns
            f"\nUser Input: {user_input}"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts information from text into JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.0
            )
            json_str = response.choices.message.content.strip()
            # GPT might wrap JSON in ```json\n...\n```
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json\n", "").replace("\n```", "")

            parameters = json.loads(json_str)
            return parameters
        except json.JSONDecodeError as e:
            print(f"Could not parse JSON from GPT for parameter extraction: {e}\nRaw GPT response: {json_str}")
            return {}
        except Exception as e:
            print(f"Error during parameter extraction: {e}")
            return {}

# Example Usage:
if __name__ == "__main__":
    nlu_service = NLUService()
    history = []
    print("AI: Hello! I can help you build a PC. What's your budget and what will you primarily use the PC for?")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # First, try to extract parameters directly
        params = nlu_service.extract_parameters(user_input, history)
        print(f"Extracted Parameters: {params}")

        # Then, get a conversational response
        ai_response, history = nlu_service.get_chat_response(user_input, history)
        print(f"AI: {ai_response}")

        # Here you would check 'params' to see if you have enough info to recommend a build
        # If params['budget'] and params['use_case'] are present, then call recommendation_service.