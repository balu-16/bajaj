# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### Files Ready
- [x] `runtime.txt` - Python 3.10.0 specified
- [x] `render.yaml` - Deployment configuration
- [x] `requirements.txt` - Dependencies optimized
- [x] `.gitignore` - Updated with deployment exclusions (local dev files excluded)
- [x] `DEPLOYMENT.md` - Comprehensive guide

### Environment Variables Required
Make sure you have these values ready for Render:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=llm-query-retrieval
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
BEARER_TOKEN=your_bearer_token
DEBUG=false
ENVIRONMENT=production
BASE_URL=https://your-app-name.onrender.com
```

### GitHub Push Commands
```bash
# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment - Add runtime.txt and optimize configs"

# Push to main
git push origin main
```

### Render Deployment Steps
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Render auto-detects `render.yaml`
5. Add environment variables
6. Click "Create Web Service"
7. Wait for build (~5-10 minutes)

### Post-Deployment Verification
- [ ] Check build logs for errors
- [ ] Test health endpoint: `https://your-app.onrender.com/health`
- [ ] Test API endpoint: `https://your-app.onrender.com/api/v1/hackrx/run`
- [ ] Verify all services initialized (Pinecone, Gemini)

### Common Issues & Solutions
1. **Build timeout**: Reduce dependencies or upgrade Render plan
2. **Memory issues**: PyTorch optimized to v2.1.0
3. **Environment variables**: Double-check all required vars are set
4. **SSL issues**: Production uses Render's SSL, no local certs needed

### Support
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
- Project Issues: Check logs in Render dashboard