# AWS Setup Helper - Step by Step Guide

## Option 1: Quick AWS CLI Installation (Windows)

### Step 1: Download AWS CLI
1. Go to: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Download the MSI installer
3. Run the installer (double-click the downloaded file)
4. Follow the installation wizard (click Next, Next, Install)
5. **Restart your terminal/PowerShell after installation**

### Step 2: Verify Installation
Open a NEW PowerShell window and run:
```powershell
aws --version
```
You should see something like: `aws-cli/2.x.x`

---

## Option 2: Install via Python (Alternative)

If the MSI installer doesn't work:
```powershell
pip install awscli
```

---

## Step 3: Get AWS Credentials

### If you DON'T have an AWS account:
1. Go to: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process (requires credit card, but free tier available)

### If you HAVE an AWS account:
1. Go to: https://console.aws.amazon.com/
2. Sign in
3. Click on your username (top right) → "Security credentials"
4. Scroll to "Access keys" section
5. Click "Create access key"
6. Choose "Command Line Interface (CLI)"
7. Click "Next" → "Create access key"
8. **IMPORTANT**: Copy both:
   - Access Key ID
   - Secret Access Key (you can only see this once!)

---

## Step 4: Configure AWS CLI

Run this command:
```powershell
aws configure
```

When prompted, enter:
1. **AWS Access Key ID**: [Paste your Access Key ID]
2. **AWS Secret Access Key**: [Paste your Secret Access Key]
3. **Default region name**: `us-east-1` (or your preferred region)
4. **Default output format**: `json` (just press Enter)

---

## Step 5: Test AWS Connection

```powershell
aws sts get-caller-identity
```

If successful, you'll see your AWS account info.

---

## Troubleshooting

### Problem: "aws: command not found"
**Solution**: 
- Restart your terminal after installing AWS CLI
- Or add AWS to PATH manually

### Problem: "Unable to locate credentials"
**Solution**: 
- Make sure you ran `aws configure`
- Check if credentials file exists: `$env:USERPROFILE\.aws\credentials`

### Problem: "Access Denied"
**Solution**: 
- Check your IAM user has proper permissions
- Make sure you copied the credentials correctly

### Problem: "Invalid credentials"
**Solution**: 
- Create new access keys in AWS Console
- Run `aws configure` again with new keys

---

## Alternative: Test Without AWS (Mock Mode)

If AWS setup is too complicated right now, I can create a version that works with local files/memory for testing. Let me know!

