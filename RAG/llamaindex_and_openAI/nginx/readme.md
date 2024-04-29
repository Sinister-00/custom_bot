## Setting up Nginx for Streamlit App on EC2

This guide will walk you through the steps to set up Nginx as a reverse proxy for your Streamlit application on an EC2 instance.

### Prerequisites

Before you begin, ensure you have the following:

- An EC2 instance running Ubuntu with Nginx installed.
- A Streamlit application running on a specific port, e.g., port 8501.
- Basic knowledge of using the terminal and editing configuration files.
- Access to your DNS provider to configure domain records.

### DNS Configuration

Before proceeding with Nginx setup, make sure to configure the following DNS records in your DNS provider's control panel:

| Type  | Name        | Content     |
| ----- | ----------- | ----------- |
| A     | sswapnil.me | 76.76.21.21 |
| CNAME | www         | sswapnil.me |

Replace `sswapnil.me` with your domain name and `76.76.21.21` with your EC2 instance's public IP address.

### Installation

First, SSH into your EC2 instance and update the package index and install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

### Configuration

1. Create a new Nginx configuration file for your Streamlit app:

```bash
sudo nano /etc/nginx/sites-available/streamlit
```

2. Add the following configuration to the file, replacing `<External_ip>` with your EC2 instance's public IP and `<internal_ip>` with the private IP of your EC2 instance along with `sswapnil.me` with your domain name:

```nginx
server {
    listen 80;
    server_name <external-ip> www.sswapnil.me sswapnil.me;

    location / {
        proxy_pass http://<internal-ip>:8501; # Forward requests to your Streamlit app running on port 8501
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

3. Create a symbolic link to enable the Nginx site configuration:

```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
```

4. Check if the Nginx configuration is valid:

```bash
sudo nginx -t
```

5. If the configuration is valid, reload Nginx to apply the changes:

```bash
sudo systemctl reload nginx
```

### Final Steps

After setting up Nginx, replace the `redirect_url` in your Streamlit application code with your server's URL:

```
http://YOUR_EC2_PUBLIC_IP/
```

### Conclusion

You have successfully configured Nginx as a reverse proxy for your Streamlit application on your EC2 instance. Now, your app should be accessible via your domain name or IP address.
