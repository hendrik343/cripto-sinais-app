import requests
import json
import sys

def send_telegram_message(token, chat_id, message):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_updates(token):
    """Get latest updates from Telegram bot"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Extract chat_ids from the updates
            if data["ok"] and data["result"]:
                print("\nDetected Chat IDs:")
                for update in data["result"]:
                    if "message" in update and "chat" in update["message"]:
                        chat = update["message"]["chat"]
                        chat_id = chat["id"]
                        chat_type = chat["type"]
                        chat_title = chat.get("title", "N/A")
                        chat_username = chat.get("username", "N/A")
                        print(f"- Chat ID: {chat_id}, Type: {chat_type}, Title: {chat_title}, Username: {chat_username}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Bot token
    token = "7773905776:AAEohw7-YUXf0RzpR7_QFfWK5_YZ_CATPi8"
    
    # Check updates first to get chat_id
    print("Checking for updates...")
    get_updates(token)
    
    print("\nSending test message...")
    # This will need to be updated with the correct chat_id from the updates
    chat_id = "5789551970"
    message = "<b>🤖 Telegram Bot Test</b>\n\nThis is a test message to verify connectivity with Telegram."
    
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
    
    success = send_telegram_message(token, chat_id, message)
    if success:
        print("Message sent successfully!")
    else:
        print("Failed to send message.")