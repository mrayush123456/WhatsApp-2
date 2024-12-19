from flask import Flask, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import threading

app = Flask(__name__)

# Global variables for user session
driver = None


@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>WhatsApp Automation</title>
        <style>
            body {
                background: rgb(240, 255, 240);
                color: rgb(34, 34, 34);
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
            }
            .container {
                background: rgb(255, 255, 255);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
                display: inline-block;
                max-width: 500px;
                text-align: left;
            }
            button {
                background-color: rgb(34, 139, 34);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: rgb(50, 205, 50);
            }
            input[type="text"], input[type="file"], input[type="number"] {
                padding: 10px;
                margin: 10px 0;
                width: 100%;
                border: 1px solid rgb(200, 200, 200);
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WhatsApp Automation</h1>
            <form action="/login" method="post">
                <button type="submit">Login to WhatsApp</button>
            </form>
            <hr>
            <form action="/send" method="post" enctype="multipart/form-data">
                <label for="target_number">Target Number (Include Country Code):</label>
                <input type="text" name="target_number" placeholder="+1234567890" required>
                
                <label for="message">Message:</label>
                <input type="text" name="message" placeholder="Type your message here" required>
                
                <label for="delay">Delay Between Messages (Seconds):</label>
                <input type="number" name="delay" min="1" max="60" value="2">
                
                <label for="text_file">Upload TXT File for Bulk Messaging (Optional):</label>
                <input type="file" name="text_file" accept=".txt">
                
                <button type="submit">Send Message</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.route('/login', methods=['POST'])
def login():
    global driver

    # Start Selenium WebDriver
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in PATH
    driver.get("https://web.whatsapp.com")
    return """
    <html>
    <head>
        <title>WhatsApp Login</title>
    </head>
    <body>
        <h1>Login to WhatsApp</h1>
        <p>Scan the QR code on the WhatsApp Web page to log in.</p>
        <a href="/">Go Back</a>
    </body>
    </html>
    """


@app.route('/send', methods=['POST'])
def send_message():
    global driver

    if not driver:
        return "Error: Please log in to WhatsApp first."

    target_number = request.form['target_number']
    message = request.form['message']
    delay = int(request.form['delay'])
    text_file = request.files.get('text_file')

    # Process bulk messages if a TXT file is provided
    if text_file:
        numbers = text_file.read().decode('utf-8').splitlines()
    else:
        numbers = [target_number]

    # Send messages
    threading.Thread(target=send_bulk_messages, args=(numbers, message, delay)).start()

    return """
    <html>
    <head>
        <title>Message Sent</title>
    </head>
    <body>
        <h1>Messages are being sent in the background!</h1>
        <a href="/">Go Back</a>
    </body>
    </html>
    """


def send_bulk_messages(numbers, message, delay):
    for number in numbers:
        try:
            # Open WhatsApp chat
            driver.get(f"https://web.whatsapp.com/send?phone={number}&text={message}")
            time.sleep(10)

            # Send the message
            send_btn = driver.find_element(By.XPATH, "//button[@data-testid='compose-btn-send']")
            send_btn.click()

            time.sleep(delay)
        except Exception as e:
            print(f"Failed to send message to {number}: {e}")


@app.route('/logout')
def logout():
    global driver
    if driver:
        driver.quit()
        driver = None
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)  
