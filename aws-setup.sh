#!/bin/bash

# AWS EC2 Setup Script for Model Playground
# This script sets up a fresh EC2 instance for running the AI model

echo "🚀 Setting up AWS EC2 instance for Model Playground..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional dependencies
echo "📦 Installing additional dependencies..."
sudo apt-get install -y git curl wget

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p ~/ModelPlayground
cd ~/ModelPlayground

# Clone or copy project files (you'll need to upload your files)
echo "📋 Project directory created at ~/ModelPlayground"
echo "📤 Please upload your project files (main.py, requirements.txt, etc.) to this directory"

# Set up firewall (optional)
echo "🔥 Setting up firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 8000/tcp # Model API
sudo ufw --force enable

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your project files to ~/ModelPlayground/"
echo "2. Run: cd ~/ModelPlayground && docker-compose up -d"
echo "3. Access your API at: http://YOUR_EC2_IP:8000"
echo ""
echo "💰 Remember to stop your EC2 instance when not in use to save costs!" 