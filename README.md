### 1. Enable required Apache modules

Run these once:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod ssl
sudo a2enmod headers
sudo systemctl restart apache2
```

---

### 2. Update VirtualHost config inside your script

Instead of:

```apache
DocumentRoot {site_path}

<Directory {site_path}>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
```

Use a **ProxyPass** and **ProxyPassReverse** block. For example, if you want to proxy to a backend app on `http://127.0.0.1:3000`:

```apache
<VirtualHost *:80>
    ServerAdmin admin@{domain}
    ServerName {domain}

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/

    ErrorLog ${APACHE_LOG_DIR}/{domain}_error.log
    CustomLog ${APACHE_LOG_DIR}/{domain}_access.log combined
</VirtualHost>
```

---

### 3. Modify your Python script

Replace the **VirtualHost section** generation with:

```python
conf_content = f"""
<VirtualHost *:80>
    ServerAdmin admin@{domain}
    ServerName {domain}

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/

    ErrorLog ${{APACHE_LOG_DIR}}/{domain}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}_access.log combined
</VirtualHost>
"""
```

💡 You can even make the **backend port** dynamic (extra script argument) so you can run:

```bash
python3 add_site.py mydomain.com 3000
```

---

### 4. HTTPS with Certbot

Your existing `certbot --apache` command will still work. It will automatically add the SSL `<VirtualHost *:443>` block and keep proxy settings.

---

### 5. Test & reload

After running your script:

```bash
sudo apache2ctl configtest
sudo systemctl reload apache2
```

---