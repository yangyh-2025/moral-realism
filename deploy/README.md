# 部署配置文档

## 概述

本目录包含ABM仿真系统的生产环境部署配置，包括Kubernetes和Terraform配置。

## 目录结构

```
deploy/
├── k8s/               # Kubernetes资源配置
│   ├── deployment.yaml   # 部署配置
│   ├── service.yaml      # 服务配置
│   ├── ingress.yaml      # Ingress配置
│.  └── secrets.yaml      # 密钥配置
├── terraform/         # Terraform基础设施配置
│   ├── main.tf          # 主配置文件
│   ├── variables.tf     # 变量定义
│   ├── outputs.tf       # 输出定义
│   └── terraform.tfvars.example  # 变量示例
└── README.md          # 本文档
```

## Kubernetes部署

### 前置条件

1. 安装 `kubectl`
2. 配置Kubernetes集群访问
3. 确保集群已安装NGINX Ingress Controller

### 部署步骤

```bash
# 1. 创建命名空间 (如果需要)
kubectl create namespace abm-simulation

# 2. 配置密钥 (编辑secrets.yaml或使用命令行创建)
kubectl create secret generic abm-secrets \
  --from-literal=database-url="postgresql://user:password@postgresql:5432/abm_simulation" \
  --from-literal=api-key="your-secret-api-key-here" \
  --from-literal=openai-api-key="your-openai-api-key-here"

# 3. 部署应用
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
kubectl apply -f deploy/k8s/ingress.yaml

# 4. 检查部署状态
kubectl get pods -l app=abm-simulation
kubectl get services
kubectl get ingress
```

### 扩容

```bash
# 手动扩容到3个副本
kubectl scale deployment abm-simulation-app --replicas=3
```

## Terraform部署

### 前置条件

1. 安装 `terraform` (>= 1.0)
2. 配置AWS CLI凭证
3. 具有AWS管理员权限或足够的IAM权限

### 部署步骤

```bash
# 1. 进入terraform目录
cd deploy/terraform

# 2. 初始化terraform
terraform init

# 3. 配置变量 (复制示例文件并编辑)
cp terraform.tfvars.example terraform.tfvars
# 编辑 terraform.tfvars 填入实际值

# 4. 查看变更计划
terraform plan

# 5. 应用变更
terraform apply -auto-approve

# 6. 获取输出信息
terraform output

# 7. 配置kubectl访问集群
aws eks update-kubeconfig --name $(terraform output -raw eks_cluster_name) --region $(terraform output -raw aws_region)
```

### 销毁资源

```bash
# 销毁所有资源 (谨慎操作!)
terraform destroy -auto-approve
```

## 备份脚本

### 使用方法

```bash
# 执行备份
./scripts/backup.sh

# 定时备份 (添加到crontab)
# 每天凌晨2点执行备份
0 2 * * * /path/to/abm-simulation/scripts/backup.sh >> /var/log/abm-backup.log 2>&1
```

## 数据库迁移

### 使用方法

```bash
# 执行数据库迁移到最新版本
./scripts/migrate.sh

# 手动使用alembic命令
alembic current           # 查看当前版本
alembic upgrade head      # 升级到最新版本
alembic downgrade base    # 降级到基线版本
alembic history           # 查看迁移历史
```

## 监控和日志

### 查看日志

```bash
# 查看应用日志
kubectl logs -f -l app=abm-simulation

# 查看特定Pod的日志
kubectl logs -f <pod-name>

# 查看最近100行日志
kubectl logs --tail=100 -l app=abm-simulation
```

### CloudWatch

Terraform会自动创建：
- CloudWatch日志组: `/aws/eks/abm-simulation-prod/application`
- CPU使用率告警
- SNS告警主题

## 安全建议

1. **密钥管理**: 使用AWS Secrets Manager或Kubernetes Secrets存储敏感信息
2. **网络隔离**: 在生产环境使用私有子网络
3. **加密**: 启用数据静态加密和传输加密
4. **访问控制**: 实施最小权限原则
5. **定期更新**: 定期更新Kubernetes和依赖组件

## 故障排查

### Pod无法启动

```bash
# 查看Pod详情
kubectl describe pod <pod-name>

# 查看Pod日志
kubectl logs <pod-name>

# 查看事件
kubectl get events --sort-by='.lastTimestamp'
```

### 服务无法访问

```bash
# 检查服务端点
kubectl get endpoints abm-simulation-service

# 检查网络策略
kubectl get networkpolicies

# 测试Pod到服务的连通性
kubectl run -it --rm debug --image=busybox -- wget -O- http://abm-simulation-service:80/api/docs
```

### 数据库连接问题

```bash
# 检查数据库Secret
kubectl describe secret abm-secrets

# 查看数据库Pod
kubectl get pods -l app=postgresql

# 检查数据库日志
kubectl logs -l app=postgresql
```

## 性能优化

### 垂直扩容

编辑 `deploy/k8s/deployment.yaml`，调整资源限制：

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### 水平扩容

使用HPA (Horizontal Pod Autoscaler)：

```bash
kubectl autoscale deployment abm-simulation-app \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

## 联系和支持

如遇到部署问题，请联系：
- Email: yangyuhang2667@163.com
- Project: ABM Simulation System

## 变更日志

- v1.0.0 (2026-03-14): 初始版本
  - 数据库连接池配置
  - 备份脚本
  - 迁移脚本
  - Kubernetes配置
  - Terraform配置
