#!/bin/bash
# Registry authentication setup

mkdir -p registry/auth

# Generate htpasswd file for Docker Registry
# Replace "dockerhub_user" and "dockerhub_password" with your credentials
docker run --entrypoint htpasswd httpd:2 -Bbn dockerhub_user dockerhub_password > registry/auth/registry.htpasswd

echo "Registry authentication configured"
echo "To login to registry from local machine:"
echo "  docker login orderscrm.ru:5000"
echo "  Username: dockerhub_user"
echo "  Password: dockerhub_password"