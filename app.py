from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from database import SessionLocal, create_db_and_tables, get_db
from services.nlu_service import NLUService
from services.recommendation_service import RecommendationService
from models import User, SavedBuild, BuildPart, Product, PriceEntry
import json
import uuid

app = Flask(__name__)
CORS(app) # Enable CORS for frontend interaction

# Initialize services
nlu_service = NLUService()
# RecommendationService will be initialized per request or via dependency injection
# in a real app, but for simplicity here we'll pass db session directly.

# Global storage for conversation history (for simplicity in MVP, real app uses session/DB)
# Key: session_id, Value: list of messages
conversation_histories = {}


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    session_id = data.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4()) # Generate a new session ID
        conversation_histories[session_id] = [] # Initialize history

    current_history = conversation_histories.get(session_id, [])

    # Get conversational response from GPT
    ai_response_text, updated_history = nlu_service.get_chat_response(user_message, current_history.copy()) # Pass a copy
    conversation_histories[session_id] = updated_history # Update history

    # Try to extract parameters for recommendation
    # This call includes the full context to give GPT enough info
    extracted_params = nlu_service.extract_parameters(user_message, updated_history)

    recommendation_output = None
    if extracted_params and extracted_params.get("budget") and extracted_params.get("use_case"):
        # We have enough info to try a recommendation
        db: Session = SessionLocal()
        rec_service = RecommendationService(db)
        build_result = rec_service.recommend_build(extracted_params)
        db.close()

        if build_result:
            # Format the recommendation for the user
            build_summary = "Here's a recommended PC build based on your preferences:\n"
            for category, item in build_result["build"].items():
                product = item["product"]
                price_entry = item["price_entry"]
                build_summary += (
                    f"- {category}: {product.name} "
                    f"(Lowest Price: ${price_entry.price:.2f} at {price_entry.retailer_name} - {price_entry.retailer_url})\n"
                )
            build_summary += f"\nTotal Estimated Cost: ${build_result['total_cost']:.2f}\n"
            build_summary += "Would you like to save this build and receive price drop notifications?"
            recommendation_output = {
                "message": build_summary,
                "build_data": {
                    "parts": [
                        {
                            "category": cat,
                            "product_id": item["product"].id,
                            "name": item["product"].name,
                            "recommended_price": item["price_entry"].price,
                            "lowest_price_retailer": item["price_entry"].retailer_name,
                            "lowest_price_url": item["price_entry"].retailer_url,
                        } for cat, item in build_result["build"].items()
                    ],
                    "total_cost": build_result["total_cost"],
                    "user_preferences": extracted_params
                }
            }
            # The AI's conversational response might already contain the recommendation,
            # we're just adding structured data for the frontend.
        else:
            # If no build found, inform the user or ask for more details
            ai_response_text += "\n\nI couldn't generate a complete build with those parameters. Could you provide more details or adjust your budget?"


    return jsonify({
        "session_id": session_id,
        "ai_message": ai_response_text,
        "extracted_parameters": extracted_params,
        "recommendation": recommendation_output
    })

@app.route("/save_build", methods=["POST"])
def save_build():
    data = request.get_json()
    user_email = data.get("email")
    user_name = data.get("name")
    build_data = data.get("build_data") # This comes from the /chat response's recommendation_output

    if not user_email or not build_data:
        return jsonify({"error": "Email and build data are required."}), 400

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(name=user_name, email=user_email)
            db.add(user)
            db.commit()
            db.refresh(user)

        saved_build = SavedBuild(
            user_id=user.id,
            user_preferences=build_data["user_preferences"] # Store original prefs
        )
        db.add(saved_build)
        db.commit()
        db.refresh(saved_build)

        for part_data in build_data["parts"]:
            build_part = BuildPart(
                saved_build_id=saved_build.id,
                product_id=part_data["product_id"],
                recommended_price=part_data["recommended_price"],
                lowest_price_retailer=part_data["lowest_price_retailer"],
                lowest_price_url=part_data["lowest_price_url"]
            )
            db.add(build_part)
        db.commit()

        return jsonify({"message": "Build saved successfully! You will receive price drop notifications.", "build_id": saved_build.id}), 201
    except Exception as e:
        db.rollback()
        print(f"Error saving build: {e}")
        return jsonify({"error": "Failed to save build."}), 500
    finally:
        db.close()

if __name__ == "__main__":
    create_db_and_tables() # Ensure DB tables are created on startup
    app.run(debug=True, port=5000)