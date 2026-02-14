#!/usr/bin/env python3
import os
import sys
import subprocess

NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"
WEB_ROOT = "/var/www"

def run_cmd(cmd):
    """Run shell commands safely."""
    print(f"👉 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def create_site(domain):
    site_path = f"{WEB_ROOT}/{domain}"

    # 1. Create project folder
    if not os.path.exists(site_path):
        run_cmd(f"sudo mkdir -p {site_path}")
        run_cmd(f"sudo chown -R $USER:$USER {site_path}")
        run_cmd(f"sudo chmod -R 755 {site_path}")

    # 2. Create sample index.php
    index_php = f"{site_path}/index.php"
    if not os.path.exists(index_php):
        with open(index_php, "w") as f:
            f.write("<?php echo 'Hello from ' . $_SERVER['SERVER_NAME']; ?>\n")

    # 3. Create Nginx server block
    conf_file = f"{NGINX_SITES_AVAILABLE}/{domain}"

    conf_content = f"""
server {{
    listen 80;
    server_name {domain};

    root {site_path};
    index index.php index.html index.htm;

    access_log /var/log/nginx/{domain}_access.log;
    error_log /var/log/nginx/{domain}_error.log;

    location / {{
        try_files $uri $uri/ =404;
    }}

    # PHP support
    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
    }}

    location ~ /\\.ht {{
        deny all;
    }}
}}
"""

    with open(f"/tmp/{domain}", "w") as f:
        f.write(conf_content)

    run_cmd(f"sudo mv /tmp/{domain} {conf_file}")

    # 4. Enable site
    run_cmd(f"sudo ln -s {conf_file} {NGINX_SITES_ENABLED}/{domain}")

    # 5. Test & reload Nginx
    run_cmd("sudo nginx -t")
    run_cmd("sudo systemctl reload nginx")

    # 6. Install SSL via Certbot
    try:
        run_cmd(
            f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos -m admin@{domain} --redirect"
        )
    except Exception as e:
        print(f"⚠️ Certbot failed for {domain}: {e}")

    print(f"\n✅ Website {domain} is ready at https://{domain}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 add_nginx_site.py yourdomain.com")
        sys.exit(1)

    domain = sys.argv[1].strip()
    create_site(domain)
