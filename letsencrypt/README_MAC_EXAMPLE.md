## README: Let's Encrypt Certificate Setup Scripts

This repository contains two Bash scripts for setting up Let's Encrypt SSL certificates using Certbot on different systems:

1. **`lets-encrypt-CA-pi-your.domain.sh`**: For Raspberry Pi or Debian-based systems (e.g., Raspbian, Ubuntu).
2. **`lets-encrypt-CA-mac-mytestdomain.sh`**: For macOS systems.

These scripts automate the process of obtaining a free SSL certificate from Let's Encrypt for a specified domain. They are tailored to their respective operating systems to ensure compatibility with package management and file system conventions.

### Prerequisites

- A domain name for which you want to obtain an SSL certificate.
- Administrative privileges on the machine where you are running the script.

### Step-by-Step Guide

#### 1. **Rename the Script File**

First, rename the script file for macOS to reflect the domain we are working with:

```bash
mv lets-encrypt-CA-mac-your.domain.sh lets-encrypt-CA-mac-mytestdomain.sh
```

#### 2. **Edit the Script for the Domain**

Open the renamed script file `lets-encrypt-CA-mac-mytestdomain.sh` in a text editor and replace the placeholders with the actual domain and email information.

```bash
nano lets-encrypt-CA-mac-mytestdomain.sh
```

Replace the following placeholders:

- **DOMAIN**: Replace `yourdomain.com` with `mytestdomain.com`.
- **Email**: Replace `your-email@example.com` with your actual email address for receiving Let's Encrypt notifications.

Here is how the modified script would look:

```bash
#!/bin/bash

# Define the domain name
DOMAIN="mytestdomain.com"

# Install Certbot if it's not already installed
if ! [ -x "$(command -v certbot)" ]; then
  echo "Certbot not found, installing..."
  brew install certbot
fi

# Obtain the Let's Encrypt certificate using Certbot
sudo certbot certonly --standalone --non-interactive --agree-tos --email admin@mytestdomain.com -d $DOMAIN

# Optional DNS-01 challenge for wildcard or specific DNS-based verification
# Uncomment the next line if you want to use DNS-01 challenge
# sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email admin@mytestdomain.com -d $DOMAIN

# Certbot will automatically place the certificates in the following directory:
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

# On macOS, /etc/ssl is usually symlinked to /private/etc/ssl, adjust paths accordingly
# Optionally, create a symbolic link for easier access (if needed for your specific server setup)
sudo ln -sf $CERT_PATH/fullchain.pem /private/etc/ssl/private/insecure.pem
sudo ln -sf $CERT_PATH/privkey.pem /private/etc/ssl/insecure.key

# Generate a DHParam file if not already existing (you can skip this if your server already has one)
if [ ! -f /private/etc/ssl/dhparam.pem ]; then
  echo "Generating DHParam file..."
  sudo openssl dhparam -out /private/etc/ssl/dhparam.pem 2048
fi

echo "SSL certificate setup with Let's Encrypt is complete."
```

#### 3. **Review Symbolic Links and Path Adjustments**

Before executing the script, it's important to understand the following lines in the script:

```bash
# On macOS, /etc/ssl is usually symlinked to /private/etc/ssl, adjust paths accordingly
# Optionally, create a symbolic link for easier access (if needed for your specific server setup)
sudo ln -sf $CERT_PATH/fullchain.pem /private/etc/ssl/private/insecure.pem
sudo ln -sf $CERT_PATH/privkey.pem /private/etc/ssl/insecure.key
```

**Explanation:**

- **Purpose of Symbolic Links**: The script creates symbolic links to the Let's Encrypt certificates in a standard location (`/private/etc/ssl/private/`). This simplifies server configuration by providing a consistent path to the most current certificates, which are automatically renewed by Let's Encrypt.
  
- **Path Adjustments on macOS**: On macOS, the `/etc/ssl` directory is typically a symlink to `/private/etc/ssl`. This distinction is important because directly referencing `/etc/ssl` might not work as expected due to the symlink. The script explicitly uses `/private/etc/ssl` to ensure the correct paths are set.

- **Commands Used**:
  - `ln -sf`: Creates or updates symbolic links. The `-s` flag creates a symbolic link, and the `-f` flag forces the update if the link already exists.
  - This ensures that the symbolic links always point to the latest certificates generated by Let's Encrypt.

#### 4. **Run the Script**

After reviewing and understanding the symbolic link setup, make the script executable and run it:

```bash
chmod +x lets-encrypt-CA-mac-mytestdomain.sh
./lets-encrypt-CA-mac-mytestdomain.sh
```

#### 5. **Script Execution and Output**

When you run the script:

- The script checks if Certbot is installed. If not, it installs Certbot using Homebrew.
- Certbot will obtain a certificate for `mytestdomain.com` using the `standalone` mode, which temporarily runs a web server on port 80.
- The script will create symbolic links to the certificate and key files in `/private/etc/ssl/private/`.
- If a Diffie-Hellman parameter file doesn't already exist, the script will generate one in `/private/etc/ssl/`.

You should see output similar to the following:

```
Certbot not found, installing...
Updating Homebrew...
==> Installing certbot from certbot/certbot
==> Downloading https://homebrew.bintray.com/bottles/certbot-1.21.0.big_sur.bottle.tar.gz
...
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mytestdomain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/mytestdomain.com/privkey.pem
This certificate expires on 2024-11-20.
These files will be updated when the certificate renews.
SSL certificate setup with Let's Encrypt is complete.
```

#### 6. **Verify the Certificate**

You can verify that the certificate has been obtained and is correctly set up by checking the symbolic links and the certificate details:

```bash
ls -l /private/etc/ssl/private/insecure.pem
ls -l /private/etc/ssl/insecure.key
```

Check the certificate details using OpenSSL:

```bash
openssl x509 -in /private/etc/ssl/private/insecure.pem -text -noout
```

#### 7. **Using the Optional DNS-01 Challenge (if Needed)**

If you need to use the DNS-01 challenge (e.g., for wildcard certificates or if your server is not publicly accessible over HTTP):

1. **Uncomment the DNS-01 line** in the script:

```bash
sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email admin@mytestdomain.com -d $DOMAIN
```

2. **Run the script again**:

```bash
./lets-encrypt-CA-mac-mytestdomain.sh
```

3. **Follow Certbot Instructions**:

- Certbot will prompt you to add a DNS TXT record to your DNS configuration:

  ```
  Please deploy a DNS TXT record under the name:

  _acme-challenge.mytestdomain.com.

  with the following value:

  WLUZg6Gv12gKP8LDptcyuxz6STRSWBsMpYkADe6djv4
  ```

- Add the TXT record to your DNS settings. You can check if the TXT record has propagated using online tools like the [Google Admin Toolbox](https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.mytestdomain.com) or [Cloudflare](https://dash.cloudflare.com/).

- After verifying the DNS TXT record has been added and propagated, press **Enter** to continue.

1. **Successful Certificate Retrieval**:

After completing the DNS-01 challenge, you should see output similar to:

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mytestdomain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/mytestdomain.com/privkey.pem
This certificate expires on 2024-12-03.
These files will be updated when the certificate renews.
```

- **Note**: Certificates obtained using the DNS-01 challenge with the `--manual` flag will not be automatically renewed. You will need to repeat the manual process to renew the certificate.

### Troubleshooting Guide

If you encounter issues during the certificate request process, refer to the following troubleshooting steps:

#### Error: Certbot Failed to Authenticate Some Domains

**Example Error Log:**

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Account registered.
Requesting a certificate for mytestdomain.com

Certbot failed to authenticate some domains (authenticator: standalone). The Certificate Authority reported these problems:
  Domain: mytestdomain.com
  Type:   connection
  Detail: 83.99.30.181: Fetching http://mytestdomain.com/.well-known/acme-challenge/sXaljI_ebryLLIJO8pQ

EFKl0uklPpq9rKg-M5x0vNgg: Error getting validation data

Hint: The Certificate Authority failed to download the challenge files from the temporary standalone webserver started by Certbot on port 80. Ensure that the listed domains point to this machine and that it can accept inbound connections from the internet.

Some challenges have failed.
Ask for help or search for solutions at https://community.letsencrypt.org. See the logfile /var/log/letsencrypt/letsencrypt.log or re-run Certbot with -v for more details.
SSL certificate setup with Let's Encrypt is complete.
```

**Common Causes and Solutions:**

1. **DNS Configuration**:
   - **Cause**: The DNS records for `mytestdomain.com` do not point to the public IP address of the machine where Certbot is running.
   - **Solution**: Verify your DNS settings and ensure the domain points to the correct public IP address.

2. **Network or Firewall Issues**:
   - **Cause**: The machine running Certbot may be behind a firewall or NAT that prevents external access to port 80.
   - **Solution**: Ensure that port 80 is open to the internet and no firewall or security group is blocking incoming traffic.

3. **Port 80 is Already in Use**:
   - **Cause**: Another service (e.g., Apache or Nginx) is already running on port 80.
   - **Solution**: Temporarily stop the service using port 80:
   
   ```bash
   sudo systemctl stop apache2   # For Apache
   sudo systemctl stop nginx     # For Nginx
   ```
   
   Re-run the script and then restart the service after obtaining the certificate.

4. **Use DNS-01 Challenge**:
   - **Cause**: If port 80 cannot be opened or is not feasible to use.
   - **Solution**: Use the DNS-01 challenge method to verify domain ownership without requiring port 80.

### Summary

By following these steps, you have successfully configured a Let's Encrypt SSL certificate for the domain `mytestdomain.com` using the macOS script. The guide ensures that you understand the symbolic link setup, path adjustments, and provides a troubleshooting guide for common issues. The optional DNS-01 challenge method is also documented for scenarios requiring DNS-based verification.
