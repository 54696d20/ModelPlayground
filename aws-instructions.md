# AWS EC2 Setup Guide for Model Playground

## 🚀 Quick Start

### 1. Launch EC2 Instance

**Recommended Instance Types:**
- **GPU Option**: `g4dn.xlarge` (4 vCPUs, 16GB RAM, 1x NVIDIA T4 GPU) - ~$0.50/hour
- **CPU Option**: `c6i.4xlarge` (16 vCPUs, 32GB RAM) - ~$0.68/hour

**Steps:**
1. Go to AWS Console → EC2 → Launch Instance
2. Choose Ubuntu Server 22.04 LTS
3. Select your preferred instance type
4. Configure Security Group:
   - SSH (Port 22) from your IP
   - Custom TCP (Port 8000) from anywhere (or your IP for security)
5. Launch and download your key pair

### 2. Connect to Your Instance

```bash
# Replace with your key and instance details
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Run Setup Script

```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/your-repo/aws-setup.sh
chmod +x aws-setup.sh
./aws-setup.sh
```

### 4. Upload Project Files

**Option A: Using SCP**
```bash
# From your local machine
scp -i your-key.pem -r . ubuntu@your-ec2-ip:~/ModelPlayground/
```

**Option B: Using Git**
```bash
# On the EC2 instance
cd ~/ModelPlayground
git clone your-repository-url .
```

### 5. Start the Application

```bash
cd ~/ModelPlayground
docker-compose -f docker-compose.aws.yml up -d
```

### 6. Access Your API

- **Health Check**: `http://your-ec2-ip:8000/health`
- **Interactive Chat**: Use the `interactive_chat.py` script locally, pointing to your EC2 IP

## 💰 Cost Optimization

### Instance Management
```bash
# Stop instance when not in use
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Start instance when needed
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### Estimated Monthly Costs (8 hours/day usage)
- **g4dn.xlarge**: ~$120/month
- **c6i.4xlarge**: ~$160/month

## 🔧 Configuration Options

### GPU Support
If using a GPU instance, update your `docker-compose.aws.yml`:
```yaml
services:
  code-generation-api:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

### Model Selection
Change the model in `docker-compose.aws.yml`:
```yaml
environment:
  - MODEL_NAME=Qwen/Qwen1.5-7B-Chat  # 7B model for better responses
  # - MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2  # Alternative
```

## 🛠️ Troubleshooting

### Check Instance Status
```bash
# Check if Docker is running
sudo systemctl status docker

# Check container logs
docker-compose -f docker-compose.aws.yml logs

# Check resource usage
htop
nvidia-smi  # If using GPU
```

### Common Issues
1. **Out of Memory**: Increase instance size or reduce model size
2. **Slow Responses**: Use GPU instance or smaller model
3. **Connection Issues**: Check security group settings

## 📊 Performance Comparison

| Instance Type | Model | Response Time | Quality | Cost/Hour |
|---------------|-------|---------------|---------|-----------|
| g4dn.xlarge   | 7B    | 2-5 seconds   | High    | $0.50     |
| c6i.4xlarge   | 7B    | 10-30 seconds | High    | $0.68     |
| c6i.2xlarge   | 3B    | 5-15 seconds  | Medium  | $0.34     |

## 🔒 Security Considerations

1. **Restrict Access**: Only allow port 8000 from your IP
2. **Use HTTPS**: Set up SSL/TLS for production
3. **Regular Updates**: Keep your instance updated
4. **Backup**: Regularly backup your model cache

## 📱 Local Access

Update your local `interactive_chat.py` to point to your EC2 instance:
```python
API_BASE_URL = "http://your-ec2-ip:8000"
``` 