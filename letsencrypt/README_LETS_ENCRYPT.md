
## README: Let's Encrypt Certificate Setup Scripts

This repository contains two Bash scripts for setting up Let's Encrypt SSL certificates using Certbot on different systems:

1. **`lets-encrypt-CA-pi-your.domain.sh`**: For Raspberry Pi or Debian-based systems (e.g., Raspbian, Ubuntu).
2. **`lets-encrypt-CA-mac-your.domain.sh`**: For macOS systems.

These scripts automate the process of obtaining a free SSL certificate from Let's Encrypt for a specified domain. They are tailored to their respective operating systems to ensure compatibility with package management and file system conventions.

### Prerequisites

- A domain name for which you want to obtain an SSL certificate.
- Administrative privileges on the machine where you are running the script.

### Usage

#### 1. For Raspberry Pi or Debian-based Systems

Use the `lets-encrypt-CA-pi-your.domain.sh` script:

```bash
./lets-encrypt-CA-pi-your.domain.sh
```

This script will:

1. Check if Certbot is installed. If not, it will install Certbot using `apt-get`.
2. Obtain a Let's Encrypt certificate using the `standalone` mode.
3. Optionally, create symbolic links for easier access to the certificate files.
4. Generate a Diffie-Hellman parameters file if it doesn't already exist.

#### 2. For macOS Systems

Use the `lets-encrypt-CA-mac-your.domain.sh` script:

```bash
./lets-encrypt-CA-mac-your.domain.sh
```

This script will:

1. Check if Certbot is installed. If not, it will install Certbot using Homebrew (`brew`).
2. Obtain a Let's Encrypt certificate using the `standalone` mode.
3. Optionally, create symbolic links for easier access to the certificate files in the macOS file system.
4. Generate a Diffie-Hellman parameters file if it doesn't already exist.

### Optional DNS-01 Challenge

Both scripts include an optional DNS-01 challenge method for obtaining the Let's Encrypt certificate. This section is commented out by default in both scripts.

**DNS-01 Challenge Command in Script:**

```bash
# sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email your-email@example.com -d $DOMAIN
```

**What is the DNS-01 Challenge?**

The DNS-01 challenge is a method used by Let's Encrypt to verify domain ownership. Unlike the HTTP-01 challenge (used in the scripts by default), which requires the server to be publicly accessible over HTTP, the DNS-01 challenge involves adding a specific DNS TXT record to your domain's DNS settings.

**Where and Why Use DNS-01 Challenge:**

- **Where**: The DNS-01 challenge can be used in environments where the HTTP-01 challenge is not feasible, such as:
  - The domain is not publicly accessible over HTTP (e.g., internal networks, restricted environments).
  - You want to issue a wildcard certificate (e.g., `*.yourdomain.com`), which requires DNS-01 verification.
- **Why**:
  - **Wildcard Certificates**: DNS-01 is the only method that allows issuing wildcard certificates.
  - **Greater Control**: You have more control over domain verification without exposing any HTTP services.
  - **Firewall or Network Restrictions**: If your environment restricts HTTP access or you are behind a firewall that doesn't allow HTTP traffic.

**How to Use DNS-01 Challenge:**

1. **Uncomment the DNS-01 Challenge Line** in the script by removing the `#` at the beginning:
   ```bash
   sudo certbot certonly --manual --preferred-challenges dns --agree-tos --email your-email@example.com -d $DOMAIN
   ```

2. **Run the Script**:
   ```bash
   ./lets-encrypt-CA-pi-your.domain.sh  # or
   ./lets-encrypt-CA-mac-your.domain.sh
   ```

3. **Follow Certbot Instructions**:
   - Certbot will provide a TXT record value that you need to add to your DNS settings for your domain.
   - Once the TXT record is added and propagated, Certbot will verify the domain and issue the certificate.

### Notes

- **Certbot Directory**: Certificates are stored in `/etc/letsencrypt/live/<yourdomain.com>/`. Ensure that you have the appropriate permissions to access and manage these files.
- **Security**: Handle your private keys (`privkey.pem`) with care and ensure they are not exposed or have insecure permissions.

### Questions and Answers

**Q: Is there any way to create a 10-year Let's Encrypt certificate?**

**A:** No, Let's Encrypt does not offer certificates with a 10-year validity. Let's Encrypt certificates have a maximum validity period of **90 days**. This short lifespan is intentional to enhance security and encourage automation. Here's why:

1. **Security**: Short-lived certificates reduce the risk associated with key compromises. If a certificate's private key is compromised, the impact is limited to a short period.
2. **Automation Encouragement**: The short validity period encourages the use of automated tools to manage certificates, reducing the risk of human error and ensuring timely renewals.
3. **Agility in Revocation**: In case of a need for revocation, short-lived certificates ensure that a potentially compromised certificate is quickly rendered invalid.

**Alternatives to Let's Encrypt for Longer Validity Certificates:**

- **Commercial Certificate Authorities (CAs)**: If you require certificates with longer validity periods (e.g., 13 months), consider purchasing them from commercial CAs like DigiCert, GlobalSign, or GoDaddy. Note that the maximum validity for publicly trusted certificates is currently set to 13 months due to CA/Browser Forum guidelines.
  
- **Private Certificate Authorities**: For internal use or environments where you control all clients, you can create your own CA and issue certificates with custom validity periods. However, these certificates won't be trusted by browsers by default, and you'll need to manually add your CA's root certificate to the trust store on each device.

**Automating Let's Encrypt Renewals:**

Given the 90-day certificate lifespan, automation is key for Let's Encrypt. Use Certbot's renewal feature to automatically renew certificates:

```bash
0 0,12 * * * /usr/bin/certbot renew --quiet
```

This cron job runs the renewal process twice a day to ensure certificates are renewed well before expiration.
