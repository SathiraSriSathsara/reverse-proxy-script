# Apache Static Site Setup Script

This repository contains a Python script to quickly set up static websites on an **Ubuntu VPS** running **Apache2**.  
The script automates:

- Creating a web root directory (`/var/www/<domain>`)
- Adding a sample `index.php`
- Creating and enabling an Apache VirtualHost
- Reloading Apache
- Optionally enabling HTTPS using **Certbot** (Let's Encrypt)

---

## 🚀 Prerequisites

Make sure your Ubuntu VPS has:

- **Apache2**
- **Certbot** (for HTTPS)
- **Python 3**

Install them with:

```bash
sudo apt update
sudo apt install apache2 python3 python3-pip certbot python3-certbot-apache -y
```


## ⚙️ Setup Apache

Enable required Apache modules:

```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

## 📂 Usage

Clone this repo to your VPS:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

Make the script executable:

```bash
chmod +x add_site.py
```

Run the script with your domain:

```bash
python3 add_site.py example.com
```

This will:

1. Create `/var/www/example.com`
2. Add a sample `index.php`
3. Create and enable Apache site config `/etc/apache2/sites-available/example.com.conf`
4. Reload Apache
5. Run Certbot to enable HTTPS (`https://example.com`)

---

## 🛠️ Example Apache Config (auto-generated)

```apache
<VirtualHost *:80>
    ServerAdmin admin@example.com
    ServerName example.com
    DocumentRoot /var/www/example.com

    <Directory /var/www/example.com>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/example.com_error.log
    CustomLog ${APACHE_LOG_DIR}/example.com_access.log combined
</VirtualHost>
```

---

## 🔐 SSL / HTTPS

If your domain points to the VPS, Certbot will automatically create an SSL certificate and configure:

```apache
<VirtualHost *:443>
    ServerName example.com
    DocumentRoot /var/www/example.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
</VirtualHost>
```

Certificates auto-renew via `certbot`.

---

## 🧹 Useful Commands

Check Apache config:

```bash
sudo apache2ctl configtest
```

Reload Apache:

```bash
sudo systemctl reload apache2
```

View logs:

```bash
tail -f /var/log/apache2/error.log
```

---

## ✅ Done

Your site should now be live at:

* `http://example.com`
* `https://example.com` (if Certbot succeeded)

```

