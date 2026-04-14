# Render Deployment Guide - NEWSLENSAI 2.0

## Prerequisites
- GitHub account with your repository pushed
- Render.com account (free tier available)
- All API keys ready:
  - `OPENAI_API_KEY`
  - `ELEVENLABS_API_KEY`
  - `D_ID_API_KEY`
  - `NEWSAPI_KEY`
  - `SECRET_KEY` (generate a random string)

---

## Step-by-Step Deployment

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Connect GitHub to Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"**
4. Search for and select your GitHub repository
5. Click **"Connect"**

### 3. Configure the Web Service

| Field | Value |
|-------|-------|
| **Name** | `newslensai` (or your preferred name) |
| **Environment** | Docker |
| **Region** | Oregon (or closest to your users) |
| **Branch** | main (or your deployment branch) |
| **Dockerfile** | Leave default or specify `./Dockerfile` |

### 4. Add Environment Variables

Click **"Advanced"** and add the following environment variables:

```
OPENAI_API_KEY = [your key]
ELEVENLABS_API_KEY = [your key]
D_ID_API_KEY = [your key]
NEWSAPI_KEY = [your key]
SECRET_KEY = [generate random string, e.g., $(openssl rand -hex 32)]
FLASK_ENV = production
```

### 5. Configure Instance Settings
- **Instance Type**: Standard ($7/month)
- **Auto-deploy**: ✓ Enable (to auto-deploy on GitHub push)
- **Health Check Path**: `/api/health`
- **Health Check Protocol**: HTTP

### 6. Deploy
1. Click **"Create Web Service"**
2. Render will start building your Docker image (takes 5-10 minutes)
3. Monitor the deployment logs in the "Logs" tab
4. Once deployed, your app URL will be displayed at the top

---

## Monitoring & Troubleshooting

### View Logs
- In Render dashboard, go to your service → **"Logs"**
- Check for any runtime errors

### Common Issues

**Issue: Build fails**
- Verify all dependencies are in `requirements.txt`
- Check that Dockerfile exists in root directory
- Ensure Python version compatibility

**Issue: App crashes after deployment**
- Check environment variables are set correctly
- Verify API keys are active and have quota
- Check logs for specific error messages

**Issue: Health check fails**
- Ensure `/api/health` endpoint is accessible
- The endpoint at `[your-url]/api/health` should return `{"status": "ok", "version": "2.0.0"}`

### Test Your Deployment
```bash
curl https://[your-render-url].onrender.com/api/health
```

Expected response:
```json
{"status": "ok", "version": "2.0.0"}
```

---

## Performance Optimization

### For Production
1. **Scaling**: Upgrade to higher instance tier if needed
2. **Caching**: Add Redis for session caching
3. **Database**: Switch from file-based to managed PostgreSQL
4. **CDN**: Enable Render's built-in CDN for static assets

### Environment Variables
- Set `FLASK_ENV=production` to disable debug mode
- Generate strong `SECRET_KEY` with: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Rolling Updates & Redeployment

**Auto-deploy on git push:**
- Enabled by default if you chose auto-deploy during setup
- Simply `git push` to trigger redeployment

**Manual redeployment:**
- In Render dashboard → Service → **"Manual Deploy"** → **"Deploy latest"**

---

## Backing Up & Persistent Storage

If you need persistent file storage (e.g., for model checkpoints):
1. Go to Service Settings → **"Disks"**
2. Add a disk for `/app/checkpoints` or `/app/static`
3. Render preserves disk data between deployments

---

## Support & Next Steps

- **Render Docs**: https://render.com/docs
- **Flask on Render**: https://render.com/docs/deploy-flask
- **Docker on Render**: https://render.com/docs/docker
- **Stuck?** Check the "Events" tab in your Render service for deployment details

---

## Your Deployment URL

Once deployed, your application will be accessible at:
```
https://[your-service-name].onrender.com
```

API endpoints will be at:
```
https://[your-service-name].onrender.com/api/[endpoint]
Frontend will be at:
https://[your-service-name].onrender.com
```

Good luck! 🚀
