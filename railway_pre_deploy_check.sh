#!/bin/bash
# Railway Pre-deployment Security Check

echo "🔍 NeuroBank FastAPI Security Pre-deployment Check"
echo "================================================="

# Check for required files
echo "📁 Checking required files..."
files=("Procfile" ".env.template" "requirements.txt" "app/main.py" "app/config.py")
missing_files=0

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        missing_files=$((missing_files + 1))
    else
        echo "✅ Found: $file"
    fi
done

if [ $missing_files -gt 0 ]; then
    echo "❌ Missing $missing_files required files. Deploy aborted."
    exit 1
fi

# Check Procfile
echo ""
echo "📋 Validating Procfile..."
if grep -q "uvicorn app.main:app" Procfile && grep -q "\$PORT" Procfile; then
    echo "✅ Procfile is correctly configured"
else
    echo "❌ Procfile configuration issues detected"
    exit 1
fi

# Check for security issues in code
echo ""
echo "🔒 Security check..."
if grep -r "allow_origins=\[\"*\"\]" app/; then
    echo "❌ CORS wildcard detected - security risk!"
    exit 1
else
    echo "✅ No CORS wildcard found"
fi

if grep -r "test-api-key" app/; then
    echo "❌ Test API key found in code - security risk!"
    exit 1
else
    echo "✅ No hardcoded test keys found"
fi

# Check Python syntax
echo ""
echo "🐍 Python syntax check..."
python3 -m py_compile app/main.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid"
else
    echo "❌ Python syntax errors detected"
    exit 1
fi

# Check requirements
echo ""
echo "📦 Checking requirements..."
if [ -f "requirements.txt" ]; then
    if grep -q "fastapi" requirements.txt && grep -q "uvicorn" requirements.txt; then
        echo "✅ Core dependencies found"
    else
        echo "❌ Missing core dependencies"
        exit 1
    fi
else
    echo "❌ requirements.txt not found"
    exit 1
fi

echo ""
echo "🎉 Security pre-deployment check completed successfully!"
echo "🚂 Ready for Railway deployment!"
echo ""
echo "🔧 Next steps:"
echo "1. Configure environment variables in Railway Dashboard:"
echo "   - API_KEY (minimum 32 characters)"
echo "   - SECRET_KEY (minimum 32 characters)"
echo "   - CORS_ORIGINS (your domain)"
echo "2. Deploy to Railway"
echo "3. Test endpoints after deployment"
