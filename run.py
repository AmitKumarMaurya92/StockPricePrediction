import os
from app import create_app

app = create_app()

# Pre-loading TensorFlow model is disabled to prevent startup timeouts and memory crashes
# The model will now lazy-load upon the first prediction request
# try:
#     from src.predict import load_model
#     print("Pre-loading TensorFlow model...")
#     load_model()
# except Exception as e:
#     print(f"Skipping model preload: {e}")

if __name__ == '__main__':
    # Run the Flask app with the port provided by environment or default to 5000
    # debug=False and use_reloader=False for maximum stability in local dev/Render
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
