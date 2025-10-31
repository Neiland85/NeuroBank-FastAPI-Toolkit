#!/bin/bash
# 🚨 Script para crear todas las CloudWatch Alarms de NeuroBank

set -e

REGION="eu-west-1"
FUNCTION_NAME="NeuroBank-Function"
API_NAME="neurobank-api"

echo "🚨 Creando CloudWatch Alarms para NeuroBank..."

# 1. High Error Rate Alarm
echo "📊 Creando alarm para High Error Rate..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-HighErrorRate" \
  --alarm-description "Lambda error rate > 1%" \
  --metric-name "Errors" \
  --namespace "AWS/Lambda" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2 \
  --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
  --treat-missing-data notBreaching \
  --region $REGION

# 2. High Latency Alarm
echo "⏱️  Creando alarm para High Latency..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-HighLatency" \
  --alarm-description "API Gateway latency > 5 seconds" \
  --metric-name "Latency" \
  --namespace "AWS/ApiGateway" \
  --statistic "Average" \
  --period 300 \
  --threshold 5000 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 1 \
  --dimensions Name=ApiName,Value=$API_NAME \
  --treat-missing-data notBreaching \
  --region $REGION

# 3. High Duration Alarm (Cost Control)
echo "💰 Creando alarm para High Duration..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-HighDuration" \
  --alarm-description "Lambda duration > 10 seconds" \
  --metric-name "Duration" \
  --namespace "AWS/Lambda" \
  --statistic "Average" \
  --period 300 \
  --threshold 10000 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2 \
  --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
  --treat-missing-data notBreaching \
  --region $REGION

# 4. High Client Errors (Security)
echo "🔒 Creando alarm para High Client Errors..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-HighClientErrors" \
  --alarm-description "High 4XX error rate - potential attack" \
  --metric-name "4XXError" \
  --namespace "AWS/ApiGateway" \
  --statistic "Sum" \
  --period 300 \
  --threshold 100 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 1 \
  --dimensions Name=ApiName,Value=$API_NAME \
  --treat-missing-data notBreaching \
  --region $REGION

# 5. Lambda Throttles
echo "🚦 Creando alarm para Lambda Throttles..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-LambdaThrottles" \
  --alarm-description "Lambda function being throttled" \
  --metric-name "Throttles" \
  --namespace "AWS/Lambda" \
  --statistic "Sum" \
  --period 300 \
  --threshold 1 \
  --comparison-operator "GreaterThanOrEqualToThreshold" \
  --evaluation-periods 1 \
  --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
  --treat-missing-data notBreaching \
  --region $REGION

# 6. No Invocations (Health Check)
echo "❤️  Creando alarm para No Invocations..."
aws cloudwatch put-metric-alarm \
  --alarm-name "NeuroBank-NoInvocations" \
  --alarm-description "No API calls in 30 minutes - possible outage" \
  --metric-name "Invocations" \
  --namespace "AWS/Lambda" \
  --statistic "Sum" \
  --period 1800 \
  --threshold 1 \
  --comparison-operator "LessThanThreshold" \
  --evaluation-periods 1 \
  --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
  --treat-missing-data breaching \
  --region $REGION

echo "✅ Todas las alarmas creadas exitosamente!"
echo ""
echo "📋 Resumen de alarmas creadas:"
echo "   1. NeuroBank-HighErrorRate"
echo "   2. NeuroBank-HighLatency"
echo "   3. NeuroBank-HighDuration"
echo "   4. NeuroBank-HighClientErrors"
echo "   5. NeuroBank-LambdaThrottles"
echo "   6. NeuroBank-NoInvocations"
echo ""
echo "🔔 Para recibir notificaciones, configurar SNS topics"
