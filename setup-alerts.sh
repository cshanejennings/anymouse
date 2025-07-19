#!/bin/bash

# Setup monitoring and alerting for Anymouse
set -e

STAGE=${1:-dev}
EMAIL=${2}
AWS_REGION=${AWS_REGION:-us-east-1}

if [ -z "$EMAIL" ]; then
  echo "❌ Usage: $0 <stage> <email>"
  echo "   Example: $0 dev admin@company.com"
  exit 1
fi

echo "📧 Setting up alerts for Anymouse $STAGE environment"
echo "📨 Email: $EMAIL"

# Get SNS topic ARN from CloudFormation outputs
TOPIC_ARN=$(aws cloudformation describe-stacks \
  --stack-name "anymouse-$STAGE" \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`AlertTopicArn`].OutputValue' \
  --output text)

if [ -z "$TOPIC_ARN" ]; then
  echo "❌ Could not retrieve SNS topic ARN from CloudFormation stack"
  echo "   Make sure the stack is deployed and contains AlertTopicArn output"
  exit 1
fi

echo "📡 SNS Topic: $TOPIC_ARN"

# Subscribe email to SNS topic
echo "📬 Subscribing $EMAIL to alerts..."
SUBSCRIPTION_ARN=$(aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint "$EMAIL" \
  --region $AWS_REGION \
  --query 'SubscriptionArn' \
  --output text)

if [ "$SUBSCRIPTION_ARN" = "pending confirmation" ]; then
  echo "✅ Email subscription created successfully"
  echo "📧 Please check your email and confirm the subscription"
  echo "   You should receive a confirmation email shortly"
else
  echo "✅ Email subscription confirmed: $SUBSCRIPTION_ARN"
fi

# Test alert by creating a test alarm
echo "🧪 Creating test alarm..."
aws cloudwatch put-metric-alarm \
  --alarm-name "anymouse-$STAGE-test-alert" \
  --alarm-description "Test alarm for Anymouse monitoring setup" \
  --metric-name "TestMetric" \
  --namespace "Anymouse/Test" \
  --statistic "Sum" \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator "GreaterThanOrEqualToThreshold" \
  --alarm-actions "$TOPIC_ARN" \
  --region $AWS_REGION

# Trigger test alarm
echo "🔔 Triggering test alert..."
aws cloudwatch put-metric-data \
  --namespace "Anymouse/Test" \
  --metric-data MetricName=TestMetric,Value=1,Unit=Count \
  --region $AWS_REGION

echo "✅ Test alert triggered!"
echo "   You should receive a test email notification shortly"
echo ""

# Cleanup test alarm after 5 minutes
echo "🧹 Test alarm will be automatically cleaned up in 5 minutes..."
(sleep 300 && aws cloudwatch delete-alarms --alarm-names "anymouse-$STAGE-test-alert" --region $AWS_REGION 2>/dev/null) &

echo "📊 Monitoring setup complete!"
echo ""
echo "🔗 Useful links:"
echo "   CloudWatch Console: https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION"
echo "   SNS Topics: https://$AWS_REGION.console.aws.amazon.com/sns/v3/home?region=$AWS_REGION#/topics"
echo "   Lambda Logs: https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups/log-group/\$252Faws\$252Flambda\$252Fanymouse-$STAGE"