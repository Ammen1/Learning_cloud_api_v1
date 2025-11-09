# Render Deployment Setup Guide

## Database Configuration (Neon.tech PostgreSQL)

Your Neon.tech PostgreSQL connection string:
```
postgresql://Ammen1:VB1jLXCZne7P@ep-billowing-water-031077-pooler.us-west-2.aws.neon.tech/helpful-tiger-64_db?sslmode=require
```

### Important Notes:
1. **Remove `channel_binding=require`** - This parameter can cause connection issues. Use only `sslmode=require`
2. **Use the pooler connection** - Your connection string uses the pooler endpoint which is recommended for serverless/cloud deployments

### Recommended Connection String for Render:
```
postgresql://Ammen1:VB1jLXCZne7P@ep-billowing-water-031077-pooler.us-west-2.aws.neon.tech/helpful-tiger-64_db?sslmode=require
```

## Render Dashboard Configuration

### Step 1: Set Environment Variables

In your Render dashboard, go to your Web Service → Environment and set:

1. **DATABASE_URL** (Required)
   ```
   postgresql://Ammen1:VB1jLXCZne7P@ep-billowing-water-031077-pooler.us-west-2.aws.neon.tech/helpful-tiger-64_db?sslmode=require
   ```

2. **SECRET_KEY** (Required)
   - Generate a secure Django secret key
   - You can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Or let Render generate it automatically (if using render.yaml)

3. **DEBUG** (Required)
   ```
   False
   ```

4. **ALLOWED_HOSTS** (Required)
   ```
   learning-cloud-api.onrender.com,localhost,127.0.0.1
   ```
   (Replace `learning-cloud-api` with your actual Render service name)

5. **PYTHON_VERSION** (Required)
   ```
   3.12.7
   ```

6. **NODE_VERSION** (Required for Prisma)
   ```
   18.x
   ```

7. **REDIS_URL** (Optional - if using Redis)
   ```
   redis://your-redis-url:6379/0
   ```

### Step 2: Build and Deploy

1. **Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```

2. **Start Command:**
   ```
   gunicorn learning_cloud.wsgi:application --bind 0.0.0.0:$PORT
   ```

3. **Health Check Path:**
   ```
   /health/
   ```

## Post-Deployment Steps

After successful deployment:

1. **Create Superuser:**
   - Use Render's shell: `render shell`
   - Run: `python manage.py createsuperuser`

2. **Verify Database Connection:**
   - Check logs for database connection errors
   - Test the health endpoint: `https://your-app.onrender.com/health/`

3. **Access API:**
   - API Docs: `https://your-app.onrender.com/api/docs/`
   - Admin Panel: `https://your-app.onrender.com/admin/`

## Troubleshooting

### Database Connection Issues

**Problem**: `FATAL: password authentication failed`

**Solution**: 
- Verify your DATABASE_URL is correct
- Check that the password doesn't contain special characters that need URL encoding
- Ensure you're using the pooler endpoint

**Problem**: `SSL connection required`

**Solution**:
- Ensure `sslmode=require` is in your connection string
- Remove `channel_binding=require` if present
- Check that your Neon.tech database allows SSL connections

**Problem**: `Connection timeout`

**Solution**:
- Verify your Neon.tech database is active (not paused)
- Check firewall settings in Neon.tech dashboard
- Ensure you're using the pooler endpoint for cloud deployments

### Build Issues

**Problem**: Pillow installation fails

**Solution**:
- Ensure PYTHON_VERSION is set to 3.12.7
- Verify requirements.txt has Pillow==10.4.0
- Clear build cache in Render dashboard

**Problem**: Migration fails

**Solution**:
- Check DATABASE_URL is set correctly
- Verify database permissions
- Check migration files are committed to repository

## Security Notes

1. **Never commit sensitive data** (passwords, secret keys) to Git
2. **Use Render's environment variables** for all secrets
3. **Enable SSL** for your Neon.tech database
4. **Use connection pooling** for better performance
5. **Rotate secrets regularly** for production

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Neon.tech Documentation](https://neon.tech/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

