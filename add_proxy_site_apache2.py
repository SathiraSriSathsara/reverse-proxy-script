#!/usr/bin/env python3
import os
import sys
import subprocess

APACHE_SITES_AVAILABLE = "/etc/apache2/sites-available"

def run_cmd(cmd):
    print(f"👉 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def create_proxy_site(domain, port):
    conf_file = f"{APACHE_SITES_AVAILABLE}/{domain}.conf"

    conf_content = f"""
<VirtualHost *:80>
    ServerName {domain}

    ErrorLog ${{APACHE_LOG_DIR}}/{domain}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}_access.log combined

    ProxyPreserveHost On

    ProxyPass / http://127.0.0.1:{port}/
    ProxyPassReverse / http://127.0.0.1:{port}/

    # WebSocket support
    RewriteEngine On
    RewriteCond %{{HTTP:Upgrade}} =websocket [NC]
    RewriteRule /(.*) ws://127.0.0.1:{port}/$1 [P,L]

    <Proxy *>
        Require all granted
    </Proxy>

    RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
"""

    # Write to temp file first
    temp_path = f"/tmp/{domain}.conf"
    with open(temp_path, "w") as f:
        f.write(conf_content)

    run_cmd(f"sudo mv {temp_path} {conf_file}")

    # Enable required Apache modules
    run_cmd("sudo a2enmod proxy")
    run_cmd("sudo a2enmod proxy_http")
    run_cmd("sudo a2enmod proxy_wstunnel")
    run_cmd("sudo a2enmod rewrite")
    run_cmd("sudo a2enmod headers")

    # Enable the site
    run_cmd(f"sudo a2ensite {domain}.conf")

    # Test Apache config
    run_cmd("sudo apache2ctl configtest")

    # Reload Apache
    run_cmd("sudo systemctl reload apache2")

    # Setup SSL with Certbot
    try:
        run_cmd(
            f"sudo certbot --apache -d {domain} --non-interactive --agree-tos -m admin@{domain} --redirect"
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
