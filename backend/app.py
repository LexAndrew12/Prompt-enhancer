from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import httpx  # Replacement for OpenAI package

app = Flask(__name__)

# Configure CORS for both endpoints
CORS(app, resources={
    r"/analyze": {
        "origins": "http://localhost:8000",
        "methods": ["POST", "OPTIONS"]
    },
    r"/optimize": {
        "origins": "http://localhost:8000",
        "methods": ["POST", "OPTIONS"]
    }
})

# Deepseek configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-b5bb033aa68b4a57a7f6750a14e1f61d')
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# Configure HTTPX client with longer timeout and retries
transport = httpx.HTTPTransport(retries=3)
client = httpx.Client(transport=transport, timeout=60.0)

@app.route('/start-analysis', methods=['POST'])
def start_analysis():
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '')
        
        # Deepseek API call
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Generate the first clarifying question to optimize this prompt:"
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.7
        }
        
        # Make synchronous HTTP request
        response = httpx.post(DEEPSEEK_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTP errors
        
        # Process Deepseek response
        ai_response = response.json()['choices'][0]['message']['content']
        
        return jsonify({
            "question": ai_response.strip()
        })
        
    except httpx.HTTPError as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/analyze', methods=['POST', 'OPTIONS'])  # Add OPTIONS method
def analyze():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing prompt in request"}), 400
            
        user_prompt = data['prompt']
        
        if len(user_prompt) > 1000:
            return jsonify({"error": "A prompt maximum 1000 karakter lehet!"}), 400
        
        # Deepseek API Call
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Analyze the prompt. Give suggestions how to enhance it to be the best AI optimized prompt! Give the answer in Hungarian!"
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.5
        }
        
        # Use persistent client with better timeout handling
        response = client.post(DEEPSEEK_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        response = jsonify({
            "analysis": response.json()['choices'][0]['message']['content']
        })
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
        return response
        
    except httpx.ReadTimeout:
        print("Deepseek API timeout")
        return jsonify({"error": "Időtúllépés az API hívásnál. Kérjük próbáld újra később."}), 504
    except httpx.HTTPError as e:
        print(f"Deepseek API error: {str(e)}")
        error_response = jsonify({"error": f"API hiba történt. Kérjük ellenőrizd a kapcsolatot."})
        error_response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
        return error_response, 502
    except Exception as e:
        print(f"Server error: {str(e)}")
        error_response = jsonify({"error": "Belső szerverhiba"})
        error_response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
        return error_response, 500

@app.route('/optimize', methods=['POST', 'OPTIONS'])
def optimize():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '')
        
        if len(user_prompt) > 1000:
            return jsonify({"error": "A prompt maximum 1000 karakter lehet!"}), 400
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Optimize the prompt to be the best AI optimized prompt! Give the answer in Hungarian!"
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            "model": "deepseek-chat",
            "temperature": 0.5
        }
        
        response = httpx.post(DEEPSEEK_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        return jsonify({
            "optimized": response.json()['choices'][0]['message']['content']
        })
        
    except Exception as e:
        print(f"Optimization error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def _build_cors_preflight_response():
    response = jsonify({"message": "Preflight Accepted"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)