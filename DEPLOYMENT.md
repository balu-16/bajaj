# Deployment Guide

This guide covers deployment to Render and local HTTPS development setup.

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- Environment variables ready
- Python 3.10.0 (specified in `runtime.txt`)

### Step 1: Prepare for GitHub Push
Before pushing to GitHub, ensure all files are ready:

**✅ Files Created/Updated:**
- `runtime.txt` - Specifies Python 3.10.0
- `render.yaml` - Render deployment configuration
- `.env.example` - Environment variables template
- `.gitignore` - Updated with deployment exclusions

### Step 2: Push to GitHub
```bash
# Check git status
git status

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Render deployment - Add runtime.txt and update configs"

# Push to main branch
git push origin main
```

### Step 3: Deploy to Render
1. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration

2. **Set Environment Variables**
   Add these in Render dashboard under "Environment":
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX_NAME=llm-query-retrieval
   GEMINI_API_KEY=your_gemini_key
   GEMINI_MODEL=gemini-1.5-flash
   BEARER_TOKEN=your_bearer_token
   DEBUG=false
   ENVIRONMENT=production
   BASE_URL=https://your-app-name.onrender.com
   ```

3. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Build time: ~5-10 minutes

### Manual Deployment Commands
If you prefer manual deployment:
```bash
# Build
pip install --upgrade pip
pip install -r requirements.txt

# Start (Render sets PORT automatically)
uvicorn main:app --host=0.0.0.0 --port=$PORT --workers=1
```

## Local HTTPS Development

### Prerequisites
- OpenSSL installed on Windows
- You can download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html

### Generate SSL Certificates

#### Option 1: Use the provided batch script
```cmd
generate_ssl.bat
```

#### Option 2: Manual OpenSSL commands
```cmd
# Generate private key
openssl genrsa -out localhost.key 2048

# Generate certificate signing request
openssl req -new -key localhost.key -out localhost.csr -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=Development/OU=IT/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in localhost.csr -signkey localhost.key -out localhost.crt

# Clean up
del localhost.csr
```

### Start HTTPS Server

#### Option 1: Use the provided batch script
```cmd
start_https.bat
```

#### Option 2: Manual Python command
```cmd
python main.py
```

#### Option 3: Direct Uvicorn command
```cmd
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile localhost.key --ssl-certfile localhost.crt
```

### Access Your Application
- Production: https://bajaj-9p8i.onrender.com
- Local Development: http://localhost:8000

### Browser Security Warning
Since you're using a self-signed certificate, your browser will show a security warning. This is normal for development. Click "Advanced" and "Proceed to localhost" to continue.

## Production Considerations

### For Render Deployment
- SSL/TLS is automatically handled by Render
- No need to include SSL certificates in production
- Environment variables should be set in Render dashboard
- The app will automatically run on HTTP in production (Render handles HTTPS termination)

### Security Notes
- Never commit SSL certificates to version control
- Use environment variables for all sensitive data
- The provided SSL certificates are for local development only
- In production, use proper SSL certificates from a trusted CA