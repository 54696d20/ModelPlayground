# Model Playground - AI Chat & Code Generation API

A FastAPI-based AI chat and code generation service that can run powerful language models on AWS EC2.

## 🚀 Features

- **AI Chat**: Interactive conversations with memory and session management
- **Code Generation**: Generate code from natural language prompts
- **AWS Deployment**: Optimized for cloud deployment with GPU support
- **Docker Containerization**: Easy deployment and scaling
- **RESTful API**: Clean API endpoints for integration

## 🏗️ Architecture

- **Backend**: FastAPI with Python 3.11
- **AI Models**: Hugging Face Transformers (Qwen, Mistral, etc.)
- **Containerization**: Docker with Docker Compose
- **Cloud**: AWS EC2 with GPU/CPU optimization
- **Client**: Python client for remote access

## 📁 Project Structure

```
ModelPlayground/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Local development setup
├── docker-compose.aws.yml # AWS-optimized setup
├── aws-setup.sh          # EC2 instance setup script
├── aws-instructions.md   # Complete AWS deployment guide
├── remote_chat.py        # Local client for AWS connection
├── interactive_chat.py   # Local development chat client
└── README.md             # This file
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ModelPlayground
   ```

2. **Start the service**
   ```bash
   docker-compose up -d
   ```

3. **Test the API**
   ```bash
   python3 interactive_chat.py
   ```

### AWS Deployment

1. **Launch EC2 Instance**
   - Use `g4dn.xlarge` (GPU) or `c6i.4xlarge` (CPU)
   - Ubuntu Server 22.04 LTS
   - Configure security group for ports 22 (SSH) and 8000 (API)

2. **Set up the instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   curl -O https://raw.githubusercontent.com/your-repo/aws-setup.sh
   chmod +x aws-setup.sh
   ./aws-setup.sh
   ```

3. **Deploy the application**
   ```bash
   # Upload files
   scp -i your-key.pem -r . ubuntu@your-ec2-ip:~/ModelPlayground/
   
   # Start the service
   ssh -i your-key.pem ubuntu@your-ec2-ip
   cd ~/ModelPlayground
   docker-compose -f docker-compose.aws.yml up -d
   ```

4. **Connect from your local machine**
   ```bash
   # Update EC2_IP in remote_chat.py
   python3 remote_chat.py
   ```

## 🔧 Configuration

### Model Selection

Edit `docker-compose.aws.yml` to change the model:

```yaml
environment:
  - MODEL_NAME=Qwen/Qwen1.5-7B-Chat  # 7B model for better responses
  # - MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2  # Alternative
  # - MODEL_NAME=Qwen/Qwen1.5-0.5B-Chat  # Smaller, faster model
```

### Resource Allocation

Adjust memory limits in `docker-compose.aws.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 16G  # Increase for larger models
    reservations:
      memory: 8G
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```
Returns service status and model information.

### Chat
```bash
POST /chat
{
  "message": "Hello, how are you?",
  "max_tokens": 512,
  "session_id": "my_session"
}
```

### Code Generation
```bash
POST /generate
{
  "prompt": "Write a Python function to sort a list",
  "max_tokens": 512
}
```

### Conversation Management
```bash
GET /conversations                    # List active sessions
DELETE /conversations/{session_id}    # Clear specific session
DELETE /conversations                 # Clear all sessions
```

## 💰 Cost Optimization

### Instance Management
```bash
# Stop when not in use
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Start when needed
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### Estimated Costs (8 hours/day usage)
- **g4dn.xlarge (GPU)**: ~$120/month
- **c6i.4xlarge (CPU)**: ~$160/month

## 🛠️ Troubleshooting

### Common Issues

1. **Out of Memory**: Increase instance size or reduce model size
2. **Slow Responses**: Use GPU instance or smaller model
3. **Connection Issues**: Check security group settings
4. **Model Loading Failures**: Ensure sufficient disk space

### Useful Commands

```bash
# Check container logs
docker-compose -f docker-compose.aws.yml logs

# Check resource usage
htop
nvidia-smi  # If using GPU

# Restart the service
docker-compose -f docker-compose.aws.yml restart
```

## 🔒 Security

- Restrict port 8000 access to your IP only
- Use HTTPS for production deployments
- Regularly update your EC2 instance
- Monitor for unusual activity

## 📊 Performance

| Instance Type | Model | Response Time | Quality | Cost/Hour |
|---------------|-------|---------------|---------|-----------|
| g4dn.xlarge   | 7B    | 2-5 seconds   | High    | $0.50     |
| c6i.4xlarge   | 7B    | 10-30 seconds | High    | $0.68     |
| c6i.2xlarge   | 3B    | 5-15 seconds  | Medium  | $0.34     |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 