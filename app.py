from flask import Flask, request, render_template_string, redirect, url_for
import requests
import time
import threading

app = Flask(__name__)

# WhatsApp Business API Endpoint
WHATSAPP_API_URL = "https://graph.facebook.com/v16.0/YOUR_PHONE_NUMBER_ID/messages"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WhatsApp Automation</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: rgb(238,174,202);
      background: linear-gradient(90deg, rgba(238,174,202,1) 0%, rgba(148,187,233,1) 100%);
      color: #333;
      padding: 20px;
    }
    .container {
      max-width: 600px;
      margin: 50px auto;
      background: #fff;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .btn {
      background-color: #007bff;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    .btn:hover {
      background-color: #0056b3;
    }
    .btn-stop {
      background-color: red;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
    .btn-stop:hover {
      background-color: darkred;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>WhatsApp Automation</h1>
    <form action="/" method="post" enctype="multipart/form-data">
      <div>
        <label for="mobile_number">Target Mobile Number:</label>
        <input type="text" id="mobile_number" name="mobile_number" required>
      </div>
      <div>
        <label for="txt_file">Upload Message File (.txt):</label>
        <input type="file" id="txt_file" name="txt_file" accept=".txt" required>
      </div>
      <div>
        <label for="hatersname">Hater's Name:</label>
        <input type="text" id="hatersname" name="hatersname" required>
      </div>
      <div>
        <label for="delay">Delay (in seconds):</label>
        <input type="number" id="delay" name="delay" required>
      </div>
      <button type="submit" class="btn">Start Sending Messages</button>
    </form>
    <form action="/stop" method="post">
      <button type="submit" class="btn-stop">Stop Sending Messages</button>
    </form>
  </div>
</body>
</html>
'''

# Global variable to control the message-sending thread
stop_thread = False

def send_messages(mobile_number, messages, hatersname, delay):
    """Send messages to a target number with a delay."""
    global stop_thread
    for message in messages:
        if stop_thread:
            print("[INFO] Message sending stopped.")
            break
        try:
            # WhatsApp API payload
            payload = {
                "messaging_product": "whatsapp",
                "to": mobile_number,
                "type": "text",
                "text": {"body": f"{hatersname}: {message}"}
            }
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"[SUCCESS] Message sent: {message}")
            else:
                print(f"[ERROR] Failed to send message: {response.json()}")

            time.sleep(delay)
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)

@app.route("/", methods=["GET", "POST"])
def index():
    global stop_thread
    if request.method == "POST":
        # Get form data
        mobile_number = request.form["mobile_number"]
        txt_file = request.files["txt_file"]
        hatersname = request.form["hatersname"]
        delay = int(request.form["delay"])

        # Read messages from uploaded .txt file
        try:
            messages = txt_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"

        # Start a new thread to send messages
        stop_thread = False
        threading.Thread(target=send_messages, args=(mobile_number, messages, hatersname, delay)).start()

        return "<p>Messages are being sent!</p>"

    return render_template_string(HTML_TEMPLATE)

@app.route("/stop", methods=["POST"])
def stop():
    global stop_thread
    stop_thread = True
    return "<p>Message sending stopped!</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
        
