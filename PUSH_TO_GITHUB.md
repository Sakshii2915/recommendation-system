# Push to GitHub Instructions

## Step 1: Create Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: `recommendation-system`
3. Description: "Real-time recommendation system with FastAPI, AWS Lambda, and DynamoDB"
4. Choose Public or Private
5. **DO NOT** check "Add a README file" (we already have one)
6. **DO NOT** add .gitignore or license (we already have them)
7. Click "Create repository"

## Step 2: Push Your Code

After creating the repository, run:

```bash
cd C:\Users\saras\Desktop\recommendation_system
git push -u origin main
```

If you're prompted for credentials:
- Use a Personal Access Token (not your password)
- Create one at: https://github.com/settings/tokens
- Select scope: `repo`

## Alternative: Use GitHub CLI

If you have GitHub CLI installed:

```bash
gh repo create recommendation-system --public --source=. --remote=origin --push
```

