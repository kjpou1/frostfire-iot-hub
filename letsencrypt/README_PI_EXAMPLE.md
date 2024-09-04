## README: Let's Encrypt Certificate Setup on Raspberry Pi (DNS-01 Challenge)

This guide explains how to set up a Let's Encrypt SSL certificate on a Raspberry Pi or Debian-based system using the DNS-01 challenge method. This method is suitable for scenarios where your domain is not publicly accessible over HTTP or when you want to obtain a wildcard certificate.

### Prerequisites

- A domain name for which you want to obtain an SSL certificate.
- Access to the domain's DNS settings to add TXT records.
- Administrative privileges on the Raspberry Pi or Debian-based system where you are running the script.

### Step-by-Step Guide

#### 1. **Prepare the Script**

Use the `lets-encrypt-CA-pi-your.domain.sh` script and modify it for your domain.

First, rename the script file to reflect the domain we are working with:

```bash
mv lets-encrypt-CA-pi-your.domain.sh lets-encrypt-CA-pi-mytestdomain.sh
```

#### 2. **Edit the Script for the Domain**

Open the renamed script file `lets-encrypt-CA-pi-mytestdomain.sh` in a text editor and replace the placeholders with the actual domain and email information.

```bash
nano lets-encrypt-CA-pi-mytestdomain.sh
```

Replace the following placeholders:

- **DOMAIN**: Replace `yourdomain.com` with `mytestdomain.com`.
- **Email**: Replace `your-email@example.com` with your actual email address for receiving Let's Encrypt notifications.

Here is how the modified script should look:

```bash
#!/bin/bash

# Define the domain name
DOMAIN="mytestdomain.com"

# Install Certbot if it's not already installed
if ! [ -x "$(command -v certbot)" ]; then
  echo "Certbot not found, installing..."
  sudo apt-get update
  sudo apt-get install certbot -y
fi

# Obtain the Let's Encrypt certificate using the DNS-01 challenge
sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email admin@mytestdomain.com -d $DOMAIN

# Certbot will automatically place the certificates in the following directory:
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

echo "SSL certificate setup with Let's Encrypt is complete."
echo "Certificate is saved at: $CERT_PATH/fullchain.pem"
echo "Key is saved at: $CERT_PATH/privkey.pem"
```

#### 3. **Run the Script**

Make the script executable and then run it:

```bash
chmod +x lets-encrypt-CA-pi-mytestdomain.sh
./lets-encrypt-CA-pi-mytestdomain.sh
```

#### 4. **Follow Certbot Instructions for DNS-01 Challenge**

When you run the script, Certbot will prompt you to add a DNS TXT record to verify domain ownership. The prompt will look similar to this:

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for mytestdomain.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name:

_acme-challenge.mytestdomain.com.

with the following value:

WLUZg6Gv12gKP8pLDgcguxz6STRSWBsMpYkADe6djv4

Before continuing, verify the TXT record has been deployed. Depending on the DNS
provider, this may take some time, from a few seconds to multiple minutes. You can
check if it has finished deploying with aid of online tools, such as the Google
Admin Toolbox: https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.mytestdomain.com.
Look for one or more bolded line(s) below the line ';ANSWER'. It should show the
value(s) you've just added.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue
```

#### 5. **Add the DNS TXT Record**

- Log in to your DNS provider's management console.
- Add a new TXT record with the name `_acme-challenge.mytestdomain.com` and the value `WLUZg6Gv12gKP8pLDgcguxz6STRSWBsMpYkADe6djv4`.
- Wait for DNS propagation. This can take a few minutes to an hour depending on your DNS provider.
- You can check the DNS propagation status using tools like the [Google Admin Toolbox](https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.mytestdomain.com) or [Cloudflare](https://dash.cloudflare.com/).

#### 6. **Complete the Certificate Request**

Once the TXT record is added and you have confirmed that it has propagated, return to your terminal and press **Enter** to continue.

Certbot will validate the DNS record and, if successful, will issue the certificate:

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mytestdomain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/mytestdomain.com/privkey.pem
This certificate expires on 2024-12-03.
These files will be updated when the certificate renews.
```

#### 7. **Verify the Certificate**

You can verify that the certificate has been obtained and is correctly set up by listing the directory:

```bash
sudo ls -al /etc/letsencrypt/live/mytestdomain.com/
```

You should see output similar to:

```
total 8
drwxr-xr-x  7 root  wheel  224 Sep  4 07:37 .
drwx------  4 root  wheel  128 Sep  4 07:37 ..
-rw-r--r--  1 root  wheel  692 Sep  4 07:37 README
lrwxr-xr-x  1 root  wheel   42 Sep  4 07:37 cert.pem -> ../../archive/mytestdomain.com/cert1.pem
lrwxr-xr-x  1 root  wheel   43 Sep  4 07:37 chain.pem -> ../../archive/mytestdomain.com/chain1.pem
lrwxr-xr-x  1 root  wheel   47 Sep  4 07:37 fullchain.pem -> ../../archive/mytestdomain.com/fullchain1.pem
lrwxr-xr-x  1 root  wheel   45 Sep  4 07:37 privkey.pem -> ../../archive/mytestdomain.com/privkey1.pem
```

### Certificate Renewal

To renew the certificate, run the script again:

```bash
./lets-encrypt-CA-pi-mytestdomain.sh
```

**Example Renewal Log Output:**

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Certificate not yet due for renewal

You have an existing certificate that has exactly the same domains or certificate name you requested and isn't close to expiry.
(ref: /etc/letsencrypt/renewal/mytestdomain.com.conf)

What would you like to do?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1: Keep the existing certificate for now
2: Renew & replace the certificate (may be subject to CA rate limits)
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
Renewing an existing certificate for mytestdomain.com

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mytestdomain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/mytestdomain.com/privkey.pem
This certificate expires on 2024-12-03.
These files will be updated when the certificate renews.

NEXT STEPS:
- This certificate will not be renewed automatically. Autorenewal of --manual certificates requires the use of an authentication hook script (--manual-auth-hook) but one was not provided. To renew this certificate, repeat this same certbot command before the certificate's expiry date.
```

### Important Notes

- **Manual Renewal**: Certificates obtained with the DNS-01 challenge using `--manual` are not automatically renewed. To renew this certificate, you will need to repeat the process before the certificate's expiry date.
- **Automation Hook**: For automatic renewal using DNS-01, you would need an authentication hook script (`--manual-auth-hook`) to automate the DNS record update, which is beyond the scope of this guide.

### Questions and Answers

**Q: Can I automate the renewal of DNS-01 challenge certificates with Certbot?**

**A:** Yes, but automating the DNS-01 challenge requires a DNS provider that supports API access. Certbot can use plugins or scripts that interact with the DNS provider's API to automatically add and remove DNS TXT records required for validation. Check Certbot's documentation or your DNS provider's API capabilities for more details on setting up automated DNS-01 challenge renewals.

### Summary

By following these steps, you have successfully configured a Let's Encrypt SSL certificate for the domain `mytestdomain.com` using the DNS-01 challenge on a Raspberry

 Pi or Debian-based system. This guide ensures secure SSL/TLS communication for environments where HTTP-01 verification is not feasible or when obtaining wildcard certificates.
