import requests
import json

# OpenRouter API key
API_KEY = "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"

# Test message
test_message = "Analyze this text: 'Today was a beautiful day. I went for a walk in the park and enjoyed the sunshine.'"

# Prepare the request payload
payload = {
    "model": "deepseek/deepseek-chat-v3.1:free",
    "messages": [
        {"role": "system", "content": "You are an AI assistant that analyzes text. Respond in French."},
        {"role": "user", "content": test_message}
    ]
}

# Make the API request
try:
    print("Sending request to OpenRouter API...")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mindscribe-journal.com",
            "X-Title": "MindScribe Journal"
        },
        data=json.dumps(payload)
    )
    
    # Check if the request was successful
    response.raise_for_status()
    
    # Parse the response
    response_data = response.json()
    ai_response = response_data["choices"][0]["message"]["content"]
    print("\nAPI Response Status Code:", response.status_code)
    print("\nAPI Response:")
    print(ai_response)
    
except requests.exceptions.HTTPError as e:
    print(f"\nHTTP Error: {e}")
    print("Response Status Code:", e.response.status_code)
    print("Response Content:", e.response.text)
except Exception as e:
    print(f"\nError: {e}")
