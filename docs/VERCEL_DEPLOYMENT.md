# 🚀 Vercel Deployment Guide

Guide for deploying BBB Medical System's separate frontends to Vercel.

## 📋 Deployment Structure

### **Separate Vercel Projects**
- **Patient Frontend**: `bbb-patient.vercel.app`
- **Doctor Frontend**: `bbb-doctor.vercel.app`
- **Backend API**: `your-backend-url.railway.app` (Railway or other services)

## 🔧 Configuration Files

### **1. Patient-specific Configuration**
```json
// vercel.patient.json
{
  "version": 2,
  "name": "bbb-patient",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-url.railway.app",
    "NEXT_PUBLIC_APP_TYPE": "patient"
  }
}
```

### **2. Doctor-specific Configuration**
```json
// vercel.doctor.json
{
  "version": 2,
  "name": "bbb-doctor",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-url.railway.app",
    "NEXT_PUBLIC_APP_TYPE": "doctor"
  }
}
```

## 🚀 Deployment Methods

### **Automatic Deployment (Using Makefile)**
```bash
# Deploy Patient Frontend only
make deploy-patient

# Deploy Doctor Frontend only
make deploy-doctor

# Deploy both frontends
make deploy-all
```

### **Manual Deployment**
```bash
# Deploy Patient Frontend
npm run deploy:patient

# Deploy Doctor Frontend
npm run deploy:doctor
```

### **Individual Vercel CLI Usage**
```bash
# Deploy Patient project
vercel --config vercel.patient.json

# Deploy Doctor project
vercel --config vercel.doctor.json
```

## 🔧 Environment Variables Setup

### **Setting up in Vercel Dashboard**
1. **Patient Project**:
   - `NEXT_PUBLIC_API_URL`: `https://your-backend-url.railway.app`
   - `NEXT_PUBLIC_APP_TYPE`: `patient`

2. **Doctor Project**:
   - `NEXT_PUBLIC_API_URL`: `https://your-backend-url.railway.app`
   - `NEXT_PUBLIC_APP_TYPE`: `doctor`

### **Setting Environment Variables via CLI**
```bash
# Patient 프로젝트
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_APP_TYPE production

# Doctor project
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_APP_TYPE production
```

## 📊 Deployment Workflow

### **1. Initial Setup**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link project
vercel link
```

### **2. Create Separate Projects**
```bash
# Create Patient project
vercel --config vercel.patient.json

# Create Doctor project
vercel --config vercel.doctor.json
```

### **3. Automatic Deployment Setup**
```bash
# GitHub integration
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_APP_TYPE production
```

## 🔍 Deployment Verification

### **Check Deployment Status**
```bash
# Check deployment status
vercel ls

# Check specific project status
vercel inspect bbb-patient
vercel inspect bbb-doctor
```

### **Check Logs**
```bash
# Patient project logs
vercel logs bbb-patient

# Doctor project logs
vercel logs bbb-doctor
```

## 🛠️ Troubleshooting

### **Common Issues**

#### 1. Build Failures
```bash
# Test build locally
npm run build:patient
npm run build:doctor

# Check Vercel logs
vercel logs --follow
```

#### 2. Environment Variable Issues
```bash
# Check environment variables
vercel env ls

# Reset environment variables
vercel env rm NEXT_PUBLIC_API_URL
vercel env add NEXT_PUBLIC_API_URL production
```

#### 3. Domain Issues
```bash
# Check domain settings
vercel domains ls

# Add domain
vercel domains add your-domain.com
```

### **Performance Optimization**

#### 1. Build Optimization
```bash
# Use build cache
vercel --prod --force

# Check build logs
vercel logs --follow
```

#### 2. Image Optimization
```bash
# Next.js image optimization settings
# Enable image optimization in next.config.ts
```

## 📈 Monitoring

### **Performance Monitoring**
- Use Vercel Analytics
- Monitor Core Web Vitals
- Track user experience metrics

### **Error Monitoring**
- Vercel Functions logs
- Client error tracking
- API response time monitoring

## 🔒 Security Settings

### **Environment Variable Security**
- Manage sensitive information with Vercel environment variables
- Use API keys only on server side

### **Domain Security**
- Force HTTPS settings
- Check CORS configuration
- Secure API endpoints

## 📚 Additional Resources

### **Documentation**
- [Vercel Official Documentation](https://vercel.com/docs)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [Environment Variables Setup](https://vercel.com/docs/environment-variables)

### **Command Reference**
```bash
# Help
make help

# Deployment commands
make deploy-patient
make deploy-doctor
make deploy-all
```
