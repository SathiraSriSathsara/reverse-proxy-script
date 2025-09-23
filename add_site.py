#!/usr/bin/env python3
import os
import sys
import subprocess

APACHE_SITES_AVAILABLE = "/etc/apache2/sites-available"
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

    # 3. Apache VirtualHost config
    conf_file = f"{APACHE_SITES_AVAILABLE}/{domain}.conf"
    conf_content = f"""
<VirtualHost *:80>
    ServerAdmin admin@{domain}
    ServerName {domain}
    DocumentRoot {site_path}

    <Directory {site_path}>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${{APACHE_LOG_DIR}}/{domain}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}_access.log combined
</VirtualHost>
"""
    with open(f"/tmp/{domain}.conf", "w") as f:
        f.write(conf_content)

    run_cmd(f"sudo mv /tmp/{domain}.conf {conf_file}")

    # 4. Enable site & reload Apache
    run_cmd(f"sudo a2ensite {domain}.conf")
    run_cmd("sudo systemctl reload apache2")

    # 5. Certbot for HTTPS
    try:
        run_cmd(f"sudo certbot --apache -d {domain} --non-interactive --agree-tos -m admin@{domain}")
    except Exception as e:
        print(f"⚠️ Certbot failed for {domain}: {e}")

    print(f"\n✅ Website {domain} is ready at https://{domain}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 add_site.py yourdomain.com")
        sys.exit(1)

    domain = sys.argv[1].strip()
    create_site(domain)
