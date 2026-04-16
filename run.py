from app import create_app

app = create_app()

# Pre-load the TensorFlow model in the main thread to prevent
# fatal thread-access segfaults (ERR_CONNECTION_RESET) on Windows/Flask
try:
    from src.predict import load_model
    print("Pre-loading TensorFlow model...")
    load_model()
except Exception as e:
    print(f"Skipping model preload: {e}")

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
