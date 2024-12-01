import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import requests  # Import requests for HTTP calls to Vectara API
import json
from types import SimpleNamespace

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Identity for the RAG agent
rag_identity = None

# Vectara API key and corpus key from environment variables
VECTARA_API_KEY = "zut_I9uYzUybNaZNP_5_LGJ13ylo8Reaxm7FRinmkA"
CORPUS_KEY = "Testing"
VECTARA_API_URL = "https://api.vectara.io/v2/chats"

# Ensure API keys are loaded
if not VECTARA_API_KEY or not CORPUS_KEY:
    logger.error("Vectara API key or corpus key not set in environment variables.")
    exit(1)

logger.info("A")

@app.route('/webhook', methods=['POST'])
def webhook():
    global rag_identity
    try:
        # Parse the incoming message
        data = request.get_data().decode('utf-8')
        message = parse_message_from_agent(data)
        #message_2 = message.payload.get("survey_responses","")
        profile = message.payload.get("profile", "")
        agent_address = message.sender
        logger.info("B")
        if not profile:
            return jsonify({"status": "error", "message": "No profile provided"}), 400
        logger.info("C")
        # Generate response based on profile
        rag_response = generate_rag_response(profile)

        # Send the response back to the client
        payload = {'rag_response': rag_response}
        send_message_to_agent(
            rag_identity,
            agent_address,
            payload
        )
        return jsonify({"status": "rag_response_sent"})

    except Exception as e:
        logger.error(f"Error in RAG agent webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def generate_rag_response(profile):
    """Generate a response based on the user profile using Vectara RAG."""
    try:
        # Use Vectara API to generate a response
        prompt = (
            f"""You are an assistant helping users who are vaccine-hesitant.
            Your goal is to provide clear, factual information to address their concerns.

            Based on the following profile, provide a response that gently informs and supports the user.
            PROFILE: {profile}

            Limit your response to 200 words.
            """
        )
        logger.info("D")
        ctx = SimpleNamespace(logger=logger)  # Create a simple context with a logger
        chat_id, response = create_chat(prompt, ctx)
        logger.info("E")
        if response:
            logger.info(f"Generated RAG response: {response}")
            return response
        else:
            logger.error("No response received from Vectara.")
            return "No response available."
    except Exception as e:
        logger.error(f"Error generating RAG response: {e}")
        return "An error occurred while generating the response."


def create_chat(query, ctx):
    url = VECTARA_API_URL

    payload = {
        "query": query,
        "search": {
            "corpora": [
                {
                    "corpus_key": CORPUS_KEY,
                    "semantics": "default"  # Using default semantics without any advanced settings
                }
            ],
            "offset": 0,
            "limit": 5  # Limiting to 5 results as a basic feature
        },
        "chat": {
            "store": True  # Store the chat message and response
        }
    }

    # Log the payload before the request, without serializing `ctx`
    #ctx.logger.info(f"Sending request to Vectara with payload: {json.dumps(payload)}")

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': VECTARA_API_KEY
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        # Log the full response details for debugging
        ctx.logger.info(f"Response status code: {response.status_code}")
        ctx.logger.info(f"Response body: {response.text}")

        if response.status_code == 200:
            chat_data = response.json()
            ctx.logger.info(f"Chat created successfully with ID: {chat_data.get('chat_id', 'N/A')}")
            return chat_data.get('chat_id'), chat_data.get('answer', '')
        else:
            ctx.logger.info(f"Failed to create chat. Status Code: {response.status_code}, Response: {response.text}")
            return None, "Failed to get response from Vectara."
    except Exception as e:
        ctx.logger.info(f"An error occurred while trying to create a chat: {e}")
        return None, f"An error occurred: {e}"


def init_agent():
    global rag_identity
    try:
        rag_identity = Identity.from_seed(os.getenv("RAG_AGENT_KEY"), 0)
        register_with_agentverse(
            identity=rag_identity,
            url="http://localhost:5009/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="RAG Agent",
            readme="""
                <description>RAG agent that provides responses based on a user profile.</description>
                <use_cases>
                    <use_case>Provide tailored recommendations or information based on a user profile.</use_case>
                </use_cases>
                <payload_requirements>
                    <description>Expects a user profile in the payload.</description>
                    <payload>
                        <requirement>
                            <parameter>profile</parameter>
                            <description>User profile generated from survey responses.</description>
                        </requirement>
                    </payload>
                </payload_requirements>
            """
        )
        logger.info("RAG agent registered successfully!")
        logger.info(f"RAG agent address: {rag_identity.address}")
    except Exception as e:
        logger.error(f"Error initializing RAG agent: {e}")
        raise


if __name__ == "__main__":
    load_dotenv()
    init_agent()
    app.run(host="0.0.0.0", port=5009, debug=True, use_reloader=False)
