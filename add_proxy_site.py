#!/usr/bin/env python3
import os
import sys
import subprocess

NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"

def run_cmd(cmd):
    print(f"👉 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def create_proxy_site(domain, port):
    conf_file = f"{NGINX_SITES_AVAILABLE}/{domain}"

    conf_content = f"""
server {{
    listen 80;
    server_name {domain};

    access_log /var/log/nginx/{domain}_access.log;
    error_log /var/log/nginx/{domain}_error.log;

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_http_version 1.1;

        # Forward headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (Socket.IO etc.)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }}
}}
"""

    # Write temp then move with sudo
    with open(f"/tmp/{domain}", "w") as f:
        f.write(conf_content)

    run_cmd(f"sudo mv /tmp/{domain} {conf_file}")

    # Enable site (symlink)
    if not os.path.exists(f"{NGINX_SITES_ENABLED}/{domain}"):
        run_cmd(f"sudo ln -s {conf_file} {NGINX_SITES_ENABLED}/{domain}")

    # Test and reload Nginx
    run_cmd("sudo nginx -t")
    run_cmd("sudo systemctl reload nginx")

    # SSL via Certbot
    try:
        run_cmd(
            f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos -m admin@{domain} --redirect"
        )
    except Exception as e:
        print(f"⚠️ Certbot failed for {domain}: {e}")

    print(f"\n✅ Reverse proxy ready: https://{domain} -> http://127.0.0.1:{port}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 add_proxy_site.py yourdomain.com 3070")
        sys.exit(1)

    domain = sys.argv[1].strip()
    port = sys.argv[2].strip()

    if not port.isdigit():
        print("❌ Port must be a number (e.g. 3070)")
        sys.exit(1)

    create_proxy_site(domain, port)
