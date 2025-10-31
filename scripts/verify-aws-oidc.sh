#!/bin/bash
# 🔐 Script de Verificación AWS OIDC para NeuroBank FastAPI Toolkit
# Account: 120242956739

set -e

echo "🔐 Verificando Configuración AWS OIDC..."
echo "Account ID: 120242956739"
echo "Region: eu-west-1"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar AWS CLI
echo "1️⃣  Verificando AWS CLI..."
if command -v aws &> /dev/null; then
    echo -e "   ${GREEN}✅ AWS CLI instalado${NC}"
    aws --version
else
    echo -e "   ${RED}❌ AWS CLI no encontrado${NC}"
    echo "   📋 Instalar: brew install awscli"
    exit 1
fi
echo ""

# Verificar configuración AWS
echo "2️⃣  Verificando configuración AWS..."
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    echo -e "   ${GREEN}✅ AWS configurado correctamente${NC}"
    echo "   📋 Account ID: $ACCOUNT"

    if [ "$ACCOUNT" = "120242956739" ]; then
        echo -e "   ${GREEN}✅ Account ID correcto${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Account ID diferente al esperado (120242956739)${NC}"
    fi
else
    echo -e "   ${RED}❌ Error de configuración AWS${NC}"
    echo "   📋 Configurar: aws configure"
    exit 1
fi
echo ""

# Verificar OIDC Provider
echo "3️⃣  Verificando OIDC Provider..."
OIDC_ARN="arn:aws:iam::120242956739:oidc-provider/token.actions.githubusercontent.com"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_ARN" &> /dev/null; then
    echo -e "   ${GREEN}✅ OIDC Provider existe${NC}"
    echo "   📋 ARN: $OIDC_ARN"
else
    echo -e "   ${RED}❌ OIDC Provider no encontrado${NC}"
    echo "   📋 Crear OIDC Provider en AWS IAM Console"
    echo "   📋 URL: token.actions.githubusercontent.com"
    echo "   📋 Audience: sts.amazonaws.com"
fi
echo ""

# Verificar IAM Role
echo "4️⃣  Verificando IAM Role..."
ROLE_NAME="GitHubActionsOIDCRole"
if aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
    echo -e "   ${GREEN}✅ IAM Role existe${NC}"
    echo "   📋 Role: $ROLE_NAME"

    # Verificar trust policy
    TRUST_POLICY=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' --output text)
    if echo "$TRUST_POLICY" | grep -q "Neiland85/NeuroBank-FastAPI-Toolkit"; then
        echo -e "   ${GREEN}✅ Trust policy configurada para el repositorio${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Verificar trust policy para Neiland85/NeuroBank-FastAPI-Toolkit${NC}"
    fi
else
    echo -e "   ${RED}❌ IAM Role no encontrado${NC}"
    echo "   📋 Crear IAM Role: GitHubActionsOIDCRole"
    echo "   📋 Trust policy para: token.actions.githubusercontent.com"
fi
echo ""

# Verificar ECR Repository
echo "5️⃣  Verificando ECR Repository..."
REPO_NAME="neurobank-fastapi"
if aws ecr describe-repositories --repository-names "$REPO_NAME" --region eu-west-1 &> /dev/null; then
    echo -e "   ${GREEN}✅ ECR Repository existe${NC}"
    echo "   📋 Repository: $REPO_NAME"
    echo "   📋 Region: eu-west-1"
else
    echo -e "   ${YELLOW}⚠️  ECR Repository se creará automáticamente${NC}"
    echo "   📋 Repository: $REPO_NAME"
fi
echo ""

echo "🎯 VERIFICACIÓN COMPLETADA"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Si todo está ✅ : Proceder con deployment"
echo "   2. Si hay ❌ : Configurar elementos faltantes en AWS"
echo "   3. Ejecutar: gh workflow run \"CI/CD Pipeline\" --ref main"
echo ""
