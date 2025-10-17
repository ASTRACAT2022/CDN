import os
import sys
import json
import requests
import time
import subprocess

# --- Configuration ---
# The URL of the admin panel should be passed as a command-line argument.
if len(sys.argv) < 2:
    print("Usage: python agent.py <admin_panel_url>")
    sys.exit(1)

ADMIN_URL = sys.argv[1].rstrip('/')
CONFIG_FILE = '/etc/cdn-agent/agent.conf'
NGINX_CONFIG_PATH = '/etc/nginx/sites-available/cdn.conf'
NGINX_ENABLED_PATH = '/etc/nginx/sites-enabled/cdn.conf'

def get_api_key():
    """Reads the API key from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        return config.get('api_key')

def save_api_key(api_key):
    """Saves the API key to the config file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'api_key': api_key}, f)

def register_node():
    """Registers the node with the admin panel and saves the API key."""
    url = f"{ADMIN_URL}/api/register/"
    print(f"Registering node with panel at {url}...")
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        api_key = data.get('api_key')
        if not api_key:
            print("Error: API key not found in registration response.")
            return None
        save_api_key(api_key)
        print("Node registered successfully. API key saved.")
        return api_key
    except requests.exceptions.RequestException as e:
        print(f"Error registering node: {e}")
        return None

def get_config(api_key):
    """Fetches the configuration from the admin panel."""
    url = f"{ADMIN_URL}/api/config/"
    headers = {'Authorization': f'ApiKey {api_key}'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching configuration: {e}")
        return None

def generate_nginx_config(websites):
    """Generates the Nginx configuration from the website list."""
    if not websites:
        return ""

    config_parts = []
    for site in websites:
        domain = site['domain']
        origin = site['origin_server']

        server_block = f"""
server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass {origin};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cache settings
        proxy_cache cdn_cache;
        proxy_cache_valid 200 302 60m;
        proxy_cache_valid 404 1m;
        add_header X-Cache-Status $upstream_cache_status;
    }}
}}
"""
        config_parts.append(server_block)

    # Add the proxy_cache_path directive once, outside of any server block.
    cache_path_config = "proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cdn_cache:10m max_size=10g inactive=60m use_temp_path=off;\n"

    return cache_path_config + "\n".join(config_parts)

def update_nginx(config_content):
    """Writes the new Nginx config and reloads Nginx."""
    try:
        with open(NGINX_CONFIG_PATH, 'w') as f:
            f.write(config_content)

        # Ensure the symlink exists
        if not os.path.lexists(NGINX_ENABLED_PATH):
             os.symlink(NGINX_CONFIG_PATH, NGINX_ENABLED_PATH)

        # Test and reload Nginx
        print("Testing Nginx configuration...")
        test_result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if test_result.returncode != 0:
            print("Nginx configuration test failed:")
            print(test_result.stderr)
            return

        print("Reloading Nginx...")
        reload_result = subprocess.run(['systemctl', 'reload', 'nginx'], capture_output=True, text=True)
        if reload_result.returncode != 0:
            print("Failed to reload Nginx:")
            print(reload_result.stderr)
        else:
            print("Nginx reloaded successfully.")

    except Exception as e:
        print(f"An error occurred during Nginx update: {e}")


def main():
    api_key = get_api_key()
    if not api_key:
        api_key = register_node()
        if not api_key:
            sys.exit(1)

    while True:
        print("Fetching latest configuration...")
        config = get_config(api_key)
        if config and 'websites' in config:
            print(f"Found {len(config['websites'])} websites to configure.")
            nginx_config = generate_nginx_config(config['websites'])
            if nginx_config:
                update_nginx(nginx_config)
            else:
                print("No websites to configure. Nginx config remains unchanged.")
        else:
            print("Could not retrieve valid config.")

        # Sleep for a while before fetching again
        time.sleep(60)

if __name__ == "__main__":
    main()