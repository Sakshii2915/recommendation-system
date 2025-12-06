"""
Quick setup verification script
Run this to check if everything is configured correctly
"""
import sys
import subprocess
import os

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.11+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = ['fastapi', 'uvicorn', 'boto3', 'numpy', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages: pip install {' '.join(missing)}")
        return False
    return True

def check_aws_cli():
    """Check if AWS CLI is configured"""
    print("\n☁️  Checking AWS CLI...")
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ AWS CLI installed: {result.stdout.strip()}")
            
            # Check if configured
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ AWS credentials configured")
                return True
            else:
                print("   ⚠️  AWS CLI installed but not configured")
                print("   Run: aws configure")
                return False
        else:
            print("   ❌ AWS CLI not found")
            return False
    except FileNotFoundError:
        print("   ❌ AWS CLI not installed")
        print("   Download from: https://aws.amazon.com/cli/")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\n📄 Checking .env file...")
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        return True
    else:
        print("   ⚠️  .env file not found")
        print("   Create .env file with:")
        print("   AWS_REGION=us-east-1")
        print("   EVENTS_TABLE_NAME=UserEvents")
        print("   RECOMMENDATIONS_TABLE_NAME=UserRecommendations")
        print("   CACHE_TABLE_NAME=RecommendationCache")
        return False

def check_dynamodb_tables():
    """Check if DynamoDB tables exist"""
    print("\n🗄️  Checking DynamoDB tables...")
    try:
        result = subprocess.run(['aws', 'dynamodb', 'list-tables'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            tables = ['UserEvents', 'UserRecommendations', 'RecommendationCache']
            output = result.stdout.lower()
            found = [t for t in tables if t.lower() in output]
            
            if len(found) == len(tables):
                print(f"   ✅ All tables exist: {', '.join(found)}")
                return True
            else:
                missing = set(tables) - set(found)
                print(f"   ⚠️  Missing tables: {', '.join(missing)}")
                print("   Run: sam build && sam deploy --guided")
                return False
        else:
            print("   ⚠️  Could not check tables (AWS credentials issue?)")
            return False
    except Exception as e:
        print(f"   ⚠️  Error checking tables: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 50)
    print("🔍 Recommendation System Setup Checker")
    print("=" * 50)
    
    checks = [
        ("Python", check_python),
        ("Dependencies", check_dependencies),
        ("AWS CLI", check_aws_cli),
        ("Environment File", check_env_file),
        ("DynamoDB Tables", check_dynamodb_tables),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n   🎉 Everything looks good! You're ready to run the application!")
        print("   Next step: uvicorn app.main:app --reload")
    else:
        print("\n   ⚠️  Some checks failed. Please fix the issues above.")
        print("   See SETUP_GUIDE.md for detailed instructions.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

