.PHONY: make_nginx

make_nginx:
    @read -p "Enter the external IP address of your EC2 instance: " external_ip; \
    read -p "Enter the internal IP address of your EC2 instance: " internal_ip; \
    read -p "Enter your domain name (e.g., example.com): " domain_name; \
    echo "Setting up Nginx for Streamlit App on EC2..."; \
    echo "Configuring DNS records..."; \
    echo "A     $(domain_name)  $(external_ip)" > dns_records.txt; \
    echo "CNAME www         $(domain_name)" >> dns_records.txt; \
    echo "DNS records configured successfully."; \
    echo "Installing Nginx..."; \
    sudo apt update && sudo apt install -y nginx; \
    echo "Configuring Nginx..."; \
    sudo bash -c 'echo "server {" > /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    listen 80;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    server_name $$external_ip www.$$domain_name $$domain_name;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    location / {" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_pass http://$$internal_ip:8501;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_http_version 1.1;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Upgrade $$http_upgrade;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Connection 'upgrade';" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Host $$host;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_cache_bypass $$http_upgrade;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    }" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "}" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "server {" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    listen 443;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    server_name $$external_ip www.$$domain_name $$domain_name;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    location / {" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_pass http://$$internal_ip:8501;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_http_version 1.1;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Upgrade $$http_upgrade;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Connection 'upgrade';" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_set_header Host $$host;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "        proxy_cache_bypass $$http_upgrade;" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "    }" >> /etc/nginx/sites-available/streamlit'; \
    sudo bash -c 'echo "}" >> /etc/nginx/sites-available/streamlit'; \
    sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/; \
    sudo nginx -t && sudo systemctl reload nginx; \
    echo "Nginx configuration complete. Your Streamlit app should now be accessible at http://$$external_ip/ and https://$$external_ip/."

