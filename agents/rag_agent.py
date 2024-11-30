import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import openai

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Identity for the RAG agent
rag_identity = None

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    global rag_identity
    try:
        # Parse the incoming message
        data = request.get_data().decode('utf-8')
        message = parse_message_from_agent(data)
        profile = message.payload.get("profile", "")
        agent_address = message.sender

        if not profile:
            return jsonify({"status": "error", "message": "No profile provided"}), 400

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
    """Generate a response based on the user profile using RAG."""
    try:
        # Use OpenAI API to generate a response
        prompt = (
            f"Given the following user profile: {profile}, "
            "provide tailored recommendations or information relevant to the user's interests and needs."
        )
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that provides recommendations based on user profiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        rag_response = response.choices[0].message.content.strip()
        logger.info(f"Generated RAG response: {rag_response}")
        return rag_response
    except Exception as e:
        logger.error(f"Error generating RAG response: {e}")
        return ""

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
    openai.api_key = os.getenv("OPENAI_API_KEY")
    init_agent()
    app.run(host="0.0.0.0", port=5009, debug=True, use_reloader=False)
