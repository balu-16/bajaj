# AWS Deployment Guide

## 🚀 Deployment Options

### Option 1: AWS App Runner (Recommended)

**Pros:** Easiest to set up, similar to Render, automatic scaling, automatic HTTPS
**Cons:** Less control, newer service

You have **two deployment methods** available:

#### Method A: Using Dockerfile (More Control)
**Steps:**
1. Go to AWS App Runner console
2. Create service from source code
3. Connect your GitHub repository
4. App Runner will automatically detect and use your `Dockerfile`
5. Set environment variables (see below)
6. Deploy!

#### Method B: Using apprunner.yaml (Simpler)
**Steps:**
1. **Remove or rename** your `Dockerfile` (App Runner prioritizes Dockerfile over apprunner.yaml)
2. Go to AWS App Runner console
3. Create service from source code
4. Connect your GitHub repository
5. Select "Use configuration file" and choose `apprunner.yaml`
6. Set environment variables (see below)
7. Deploy!

**Note:** If both files exist, App Runner will use the `Dockerfile` and ignore `apprunner.yaml`. Choose one method based on your preference.

### Option 2: AWS Elastic Beanstalk

**Pros:** More mature, good monitoring, easy scaling
**Cons:** Slightly more complex setup

**Steps:**
1. Install AWS CLI and EB CLI
2. Run `eb init` in project directory
3. Run `eb create production`
4. Set environment variables via EB console
5. Deploy with `eb deploy`

### Option 3: AWS ECS with Fargate

**Pros:** Most scalable, production-ready, containerized
**Cons:** Requires Docker knowledge, more complex

**Steps:**
1. Build Docker image: `docker build -t bajaj-api .`
2. Push to ECR (Elastic Container Registry)
3. Create ECS cluster and service
4. Configure load balancer and auto-scaling

## 🔧 Required Environment Variables

Set these in your AWS service:

```
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=llm-query-retrieval

# AI Services
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
OPENAI_API_KEY=your_openai_api_key

# Authentication
BEARER_TOKEN=your_bearer_token

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
BASE_URL=https://xivn9ims7c.ap-south-1.awsapprunner.com
TIMEZONE=Asia/Kolkata
```

## 💰 Cost Comparison

| Service | Estimated Monthly Cost | Best For |
|---------|----------------------|----------|
| App Runner | $7-25 | Small to medium apps |
| Elastic Beanstalk | $10-50 | Traditional web apps |
| ECS Fargate | $15-100+ | High-scale production |

## 🔍 Monitoring & Logs

- **CloudWatch**: Automatic logging and monitoring
- **X-Ray**: Distributed tracing (optional)
- **Health Checks**: Built-in endpoint monitoring

## 🚨 Security Best Practices

1. Use AWS Secrets Manager for API keys
2. Enable VPC for database connections
3. Use IAM roles instead of access keys
4. Enable CloudTrail for audit logging
5. Set up WAF for API protection

## 📊 Performance Optimization

1. Use CloudFront CDN for static assets
2. Enable auto-scaling based on CPU/memory
3. Use RDS Proxy for database connections
4. Implement caching with ElastiCache

## 🔄 CI/CD Pipeline

Consider setting up AWS CodePipeline for automatic deployments:
1. Code commit triggers pipeline
2. CodeBuild runs tests
3. Automatic deployment to staging
4. Manual approval for production