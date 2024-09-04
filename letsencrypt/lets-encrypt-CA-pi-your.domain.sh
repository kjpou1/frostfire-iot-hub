#!/bin/bash

# Define the domain name
DOMAIN="yourdomain.com"

# Install Certbot if it's not already installed
if ! [ -x "$(command -v certbot)" ]; then
  echo "Certbot not found, installing..."
  sudo apt-get update
  sudo apt-get install certbot -y
fi

# Obtain the Let's Encrypt certificate using Certbot
sudo certbot certonly --standalone --non-interactive --agree-tos --email your-email@example.com -d $DOMAIN

# Obtain the Let's Encrypt certificate using the DNS-01 challenge with Certbot
# sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email your-email@example.com -d $DOMAIN

# Certbot will automatically place the certificates in the following directory:
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

# Optionally, create a symbolic link for easier access (if needed for your specific server setup)
sudo ln -sf $CERT_PATH/fullchain.pem /etc/ssl/private/insecure.pem
sudo ln -sf $CERT_PATH/privkey.pem /etc/ssl/insecure.key

# Generate a DHParam file if not already existing (you can skip this if your server already has one)
if [ ! -f /etc/ssl/dhparam.pem ]; then
  echo "Generating DHParam file..."
  sudo openssl dhparam -out /etc/ssl/dhparam.pem 2048
fi

echo "SSL certificate setup with Let's Encrypt is complete."
