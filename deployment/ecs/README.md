# ECS Service Definition for Apigee Hybrid MCP Server

## Prerequisites

1. **IAM Roles**:
   - ECS Task Execution Role with permissions:
     - AmazonECSTaskExecutionRolePolicy
     - Secrets Manager access
     - ECR access
   - ECS Task Role with permissions:
     - Google Cloud API access (if using federation)

2. **Secrets in AWS Secrets Manager**:
   ```bash
   # Create secrets
   aws secretsmanager create-secret \
     --name apigee-mcp/google-project-id \
     --secret-string "your-project-id"
   
   aws secretsmanager create-secret \
     --name apigee-mcp/organization \
     --secret-string "your-org-name"
   
   aws secretsmanager create-secret \
     --name apigee-mcp/credentials-path \
     --secret-string "/app/credentials/service-account.json"
   ```

3. **ECR Repository**:
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name apigee-hybrid-mcp
   
   # Build and push image
   docker build -t apigee-hybrid-mcp .
   docker tag apigee-hybrid-mcp:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/apigee-hybrid-mcp:latest
   aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
   docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/apigee-hybrid-mcp:latest
   ```

## Deployment Steps

1. **Update task-definition.json**:
   - Replace `ACCOUNT_ID` with your AWS account ID
   - Replace `REGION` with your AWS region
   - Update ARNs for roles and secrets

2. **Register task definition**:
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

3. **Create ECS service**:
   ```bash
   aws ecs create-service \
     --cluster your-cluster-name \
     --service-name apigee-hybrid-mcp \
     --task-definition apigee-hybrid-mcp:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=DISABLED}" \
     --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT_ID:targetgroup/apigee-mcp/xxx,containerName=apigee-mcp-server,containerPort=8080"
   ```

4. **Update service** (for new versions):
   ```bash
   aws ecs update-service \
     --cluster your-cluster-name \
     --service apigee-hybrid-mcp \
     --force-new-deployment
   ```

## Monitoring

1. **CloudWatch Logs**:
   ```bash
   aws logs tail /ecs/apigee-hybrid-mcp --follow
   ```

2. **Service metrics**:
   - CPU utilization
   - Memory utilization
   - Task count
   - Failed health checks

## Scaling

Auto-scaling configuration:
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/your-cluster-name/apigee-hybrid-mcp \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/your-cluster-name/apigee-hybrid-mcp \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Troubleshooting

1. **Task fails to start**:
   - Check execution role permissions
   - Verify secrets exist and are accessible
   - Check ECR image is accessible

2. **Health checks failing**:
   - Verify application is starting correctly
   - Check CloudWatch logs for errors
   - Ensure health check command is correct

3. **Service unavailable**:
   - Check target group health
   - Verify security group rules
   - Check load balancer configuration
