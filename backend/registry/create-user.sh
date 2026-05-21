#!/bin/bash

# Create user for Docker Registry
# Usage: ./create-user.sh <username> <password>

USERNAME="${1:-admin}"
PASSWORD="${2:-crm_password}"

mkdir -p auth

# Generate htpasswd file
docker run --entrypoint htpasswd httpd:2 -Bbn "$USERNAME" "$PASSWORD" > auth/registry.htpasswd

echo "User '$USERNAME' created successfully!"
echo "To login: docker login orderscrm.ru:5000"