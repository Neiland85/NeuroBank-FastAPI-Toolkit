# 📊 Monitoring & Alerting Setup - NeuroBank FastAPI Toolkit

## 🎯 **Estrategia de Monitoreo**

### **📈 Key Performance Indicators (KPIs)**

#### **🚀 Performance Metrics**
- **Response Time**: < 200ms promedio
- **Throughput**: Requests/second sostenible
- **Error Rate**: < 0.1% en producción
- **Cold Start**: < 3 segundos Lambda

#### **💰 Cost Metrics**
- **Lambda Duration**: Optimización de costos
- **API Gateway Requests**: Límites de usage plan
- **CloudWatch Logs**: Retención optimizada
- **Data Transfer**: Minimizar costs entre AZs

#### **🔒 Security Metrics**
- **Failed Authentication**: Intentos maliciosos
- **Rate Limit Hits**: Protección DDoS
- **API Key Usage**: Patrones de consumo
- **Error Patterns**: Detección de ataques

---

## 📊 **CloudWatch Dashboard Configuration**

### **Dashboard JSON Template**

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "NeuroBank-Function"],
          [".", "Invocations", ".", "."],
          [".", "Errors", ".", "."],
          [".", "Throttles", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "eu-west-1",
        "title": "Lambda Performance"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApiGateway", "4XXError", "ApiName", "neurobank-api"],
          [".", "5XXError", ".", "."],
          [".", "Latency", ".", "."],
          [".", "Count", ".", "."]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "eu-west-1",
        "title": "API Gateway Metrics"
      }
    }
  ]
}
```

### **Crear Dashboard via AWS CLI**

```bash
# Crear dashboard personalizado
aws cloudwatch put-dashboard \
  --dashboard-name "NeuroBank-Production-Dashboard" \
  --dashboard-body file://monitoring/dashboard-config.json \
  --region eu-west-1

# Verificar dashboard
aws cloudwatch list-dashboards --region eu-west-1
```

---

## 🚨 **CloudWatch Alarms Setup**

### **1. 🚀 Performance Alarms**

```bash
# Alarm para High Error Rate
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
  --dimensions Name=FunctionName,Value=NeuroBank-Function \
  --region eu-west-1

# Alarm para High Latency
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
  --dimensions Name=ApiName,Value=neurobank-api \
  --region eu-west-1
```

### **2. 💰 Cost Control Alarms**

```bash
# Alarm para Lambda Duration (cost control)
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
  --dimensions Name=FunctionName,Value=NeuroBank-Function \
  --region eu-west-1
```

### **3. 🔒 Security Alarms**

```bash
# Alarm para 4XX Errors (potential attacks)
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
  --dimensions Name=ApiName,Value=neurobank-api \
  --region eu-west-1
```

---

## 📧 **SNS Notification Setup**

### **Email Notifications**

```bash
# Crear SNS topic para alertas
aws sns create-topic \
  --name "NeuroBank-Alerts" \
  --region eu-west-1

# Obtener ARN del topic
TOPIC_ARN=$(aws sns list-topics --region eu-west-1 --query 'Topics[?contains(TopicArn,`NeuroBank-Alerts`)].TopicArn' --output text)

# Suscribir email para notificaciones
aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint "your-email@domain.com" \
  --region eu-west-1

# Confirmar suscripción (check email)
```

### **Slack Integration (Opcional)**

```bash
# Crear Lambda function para Slack notifications
# Webhook URL: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol lambda \
  --notification-endpoint "arn:aws:lambda:eu-west-1:120242956739:function:SlackNotifier" \
  --region eu-west-1
```

---

## 🔍 **Custom Log Insights Queries**

### **Performance Analysis**

```sql
-- Top slow requests
fields @timestamp, @message, @duration
| filter @message like /START RequestId/
| stats avg(@duration) as avg_duration by bin(5m)
| sort @timestamp desc
| limit 100

-- Error pattern analysis
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(1h)
| sort @timestamp desc
```

### **Security Analysis**

```sql
-- Authentication failures
fields @timestamp, @message
| filter @message like /401/ or @message like /403/
| stats count() as auth_failures by bin(1h)
| sort @timestamp desc

-- Rate limit monitoring
fields @timestamp, @message
| filter @message like /rate.limit/
| stats count() as rate_limits by bin(1h)
| sort @timestamp desc
```

---

## 📱 **Mobile Dashboard Access**

### **CloudWatch Mobile App**
1. **Install**: AWS Console Mobile App
2. **Login**: AWS Account 120242956739
3. **Navigate**: CloudWatch > Dashboards
4. **Select**: NeuroBank-Production-Dashboard
5. **Pin**: Add to favorites for quick access

---

## 🎯 **Monitoring Automation Script**

```bash
#!/bin/bash
# monitoring/setup-monitoring.sh

echo "📊 Setting up NeuroBank Monitoring..."

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "NeuroBank-Production" \
  --dashboard-body file://monitoring/dashboard.json \
  --region eu-west-1

# Setup alarms
./monitoring/create-alarms.sh

# Setup SNS notifications
./monitoring/setup-notifications.sh

echo "✅ Monitoring setup complete!"
echo "🎯 Access dashboard: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-1#dashboards:name=NeuroBank-Production"
```

---

## 📈 **Business Intelligence Metrics**

### **📊 Usage Analytics**
- **Daily Active Users**: Unique API key usage
- **Popular Endpoints**: Most frequently called
- **Peak Hours**: Traffic patterns
- **Geographic Distribution**: Request origins

### **💡 Performance Insights**
- **Response Time Trends**: Weekly/monthly analysis
- **Error Rate Patterns**: Seasonal variations
- **Cost Per Transaction**: Business efficiency
- **SLA Compliance**: 99.9% uptime target

---

## 🚨 **Incident Response Playbook**

### **Severity Levels**

#### **🔴 P0 - Critical (< 15 min response)**
- Complete service outage
- Security breach detected
- Data integrity issues

#### **🟡 P1 - High (< 1 hour response)**
- Performance degradation > 50%
- Error rate > 5%
- Authentication failures spike

#### **🟢 P2 - Medium (< 4 hours response)**
- Minor performance issues
- Non-critical feature failures
- Capacity warnings

### **Response Actions**
1. **Immediate**: Check dashboards and logs
2. **Investigate**: Root cause analysis
3. **Communicate**: Status page updates
4. **Resolve**: Fix and validate
5. **Post-mortem**: Lessons learned

---

## 🎉 **Success Metrics**

### **✅ Production Ready Indicators**
- [ ] All dashboards operational
- [ ] Alarms configured and tested
- [ ] Notification channels active
- [ ] Log insights queries saved
- [ ] Incident response tested
- [ ] Cost monitoring active
- [ ] Performance baselines established

**🎯 Monitoring completamente configurado y listo para producción!**
