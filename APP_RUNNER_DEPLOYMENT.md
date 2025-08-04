# 🚀 AWS App Runner Deployment Guide

## Overview
AWS App Runner is a fully managed service that makes it easy to deploy web applications and APIs at scale. It automatically handles:
- ✅ **Load balancing**
- ✅ **Auto-scaling**
- ✅ **SSL/TLS certificates**
- ✅ **Health checks**
- ✅ **CI/CD from GitHub**

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **GitHub Repository** with your code
3. **Domain** (optional, for custom domain)

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push to GitHub
```bash
git add .
git commit -m "Prepare for App Runner deployment"
git push origin main
```

### 1.2 Verify Files
Ensure these files are in your repository:
- ✅ `main.py` (entry point)
- ✅ `requirements.txt` (dependencies)
- ✅ `apprunner.yaml` (App Runner configuration)
- ✅ `Dockerfile` (optional, for custom control)

## 🚀 Step 2: Deploy via AWS Console

### 2.1 Navigate to App Runner
1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Click **"Create service"**

### 2.2 Configure Source
1. **Source type**: Repository
2. **Repository provider**: GitHub
3. **Connect to GitHub**: 
   - Click "Add new"
   - Authorize AWS Connector for GitHub
   - Select your repository
4. **Branch**: `main`
5. **Deployment trigger**: Automatic (deploys on every push)

### 2.3 Configure Build
1. **Configuration file**: Use configuration file (`apprunner.yaml`)
2. App Runner will automatically detect your `apprunner.yaml`

### 2.4 Configure Service
1. **Service name**: `bajaj-api-service`
2. **Virtual CPU**: 1 vCPU
3. **Memory**: 2 GB
4. **Environment variables**:
   ```
   GEMINI_API_KEY=your_gemini_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_pinecone_env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   JWT_SECRET_KEY=your_jwt_secret
   ```

### 2.5 Configure Auto Scaling (Optional)
- **Min instances**: 1
- **Max instances**: 10
- **Concurrency**: 100 requests per instance

### 2.6 Configure Health Check
- **Path**: `/health`
- **Interval**: 10 seconds
- **Timeout**: 5 seconds
- **Healthy threshold**: 2
- **Unhealthy threshold**: 5

## 🔐 Step 3: Environment Variables Setup

### 3.1 Using AWS Systems Manager (Recommended)
```bash
# Store secrets in AWS Systems Manager Parameter Store
aws ssm put-parameter --name "/bajaj-api/gemini-api-key" --value "your_key" --type "SecureString"
aws ssm put-parameter --name "/bajaj-api/pinecone-api-key" --value "your_key" --type "SecureString"
```

### 3.2 Reference in App Runner
In the App Runner console, add environment variables:
```
GEMINI_API_KEY={{resolve:ssm-secure:/bajaj-api/gemini-api-key}}
PINECONE_API_KEY={{resolve:ssm-secure:/bajaj-api/pinecone-api-key}}
```

## 🌐 Step 4: Custom Domain (Optional)

### 4.1 Add Custom Domain
1. In App Runner service, go to **"Custom domains"**
2. Click **"Link domain"**
3. Enter your domain: `api.yourdomain.com`
4. App Runner will provide CNAME records

### 4.2 Update DNS
Add CNAME record in your DNS provider:
```
CNAME: api.yourdomain.com → [app-runner-domain].awsapprunner.com
```

## 📊 Step 5: Monitoring & Logging

### 5.1 CloudWatch Integration
App Runner automatically sends logs to CloudWatch:
- **Application logs**: `/aws/apprunner/[service-name]/application`
- **Service logs**: `/aws/apprunner/[service-name]/service`

### 5.2 Metrics Available
- **Request count**
- **Response time**
- **HTTP status codes**
- **Active instances**
- **CPU/Memory utilization**

## 🔄 Step 6: CI/CD Workflow

### 6.1 Automatic Deployment
Every push to `main` branch triggers:
1. **Build**: App Runner builds using `apprunner.yaml`
2. **Test**: Health checks validate deployment
3. **Deploy**: Traffic switches to new version
4. **Rollback**: Automatic rollback on failure

### 6.2 Manual Deployment
```bash
# Trigger manual deployment
aws apprunner start-deployment --service-arn [your-service-arn]
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs in CloudWatch
aws logs describe-log-groups --log-group-name-prefix "/aws/apprunner"
```

#### 2. Health Check Failures
- Verify `/health` endpoint returns 200
- Check application logs for errors
- Ensure correct port (8000) is exposed

#### 3. Environment Variables
- Use AWS Systems Manager for secrets
- Verify variable names match your code
- Check CloudWatch logs for missing variables

### Debug Commands
```bash
# Get service status
aws apprunner describe-service --service-arn [your-service-arn]

# View recent deployments
aws apprunner list-operations --service-arn [your-service-arn]

# Check logs
aws logs tail /aws/apprunner/[service-name]/application --follow
```

## 💰 Cost Optimization

### 5.1 Right-sizing
- Start with 1 vCPU, 2GB RAM
- Monitor CPU/Memory usage
- Scale based on actual needs

### 5.2 Auto-scaling
- Set appropriate min/max instances
- Use concurrency settings to optimize costs
- Monitor request patterns

## 🔒 Security Best Practices

### 6.1 Environment Variables
- ✅ Use AWS Systems Manager Parameter Store
- ✅ Never commit secrets to Git
- ✅ Rotate keys regularly

### 6.2 Network Security
- ✅ App Runner provides HTTPS by default
- ✅ Use VPC connector for database access
- ✅ Implement rate limiting in your app

## 📈 Performance Optimization

### 7.1 Application Level
- Use async/await for I/O operations
- Implement connection pooling
- Add caching where appropriate

### 7.2 App Runner Level
- Configure appropriate instance size
- Set optimal concurrency limits
- Use health checks effectively

## 🎯 Success Criteria

After deployment, verify:
- ✅ **HTTPS endpoint** is accessible
- ✅ **Health check** returns 200
- ✅ **API endpoints** work correctly
- ✅ **Auto-deployment** triggers on push
- ✅ **Logs** appear in CloudWatch
- ✅ **Metrics** show in App Runner console

## 📞 Support & Resources

- **AWS App Runner Documentation**: https://docs.aws.amazon.com/apprunner/
- **Pricing Calculator**: https://calculator.aws/
- **GitHub Integration**: https://docs.aws.amazon.com/apprunner/latest/dg/manage-connections.html

---

## 🚀 Quick Start Commands

```bash
# 1. Push to GitHub
git add . && git commit -m "Deploy to App Runner" && git push

# 2. Create App Runner service (via AWS CLI)
aws apprunner create-service \
  --service-name "bajaj-api" \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "public.ecr.aws/aws-containers/hello-app-runner:latest",
      "ImageConfiguration": {
        "Port": "8000"
      },
      "ImageRepositoryType": "ECR_PUBLIC"
    },
    "AutoDeploymentsEnabled": true
  }'

# 3. Check deployment status
aws apprunner describe-service --service-arn [your-service-arn]
```

Your FastAPI application will be available at:
`https://[random-id].awsapprunner.com`