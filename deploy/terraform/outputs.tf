# Terraform输出定义
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR"
  value       = module.vpc.vpc_cidr
}

output "private_subnet_ids" {
  description = "私有子网IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "公共子网IDs"
  value       = module.vpc.public_subnets
}

output "eks_cluster_id" {
  description = "EKS集群ID"
  value       = module.eks.cluster_id
}

output "eks_cluster_name" {
  description = "EKS集群名称"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS集群端点"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_certificate" {
  description = "EKS集群证书"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_cluster_security_group_id" {
  description = "EKS集群安全组ID"
  value       = module.eks.cluster_security_group_id
}

output "ecr_repository_url" {
  description = "ECR仓库URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_repository_name" {
  description = "ECR仓库名称"
  value       = aws_ecr_repository.app.name
}

output "rds_endpoint" {
  description = "RDS数据库端点"
  value       = module.db.db_instance_endpoint
}

output "rds_instance_id" {
  description = "RDS实例ID"
  value       = module.db.db_instance_id
}

output "rds_port" {
  description = "RDS端口"
  value       = module.db.db_instance_port
}

output "s3_backups_bucket" {
  description = "S3备份存储桶"
  value       = aws_s3_bucket.backups.id
}

output "s3_logs_bucket" {
  description = "S3日志存储桶"
  value       = aws_s3_bucket.logs.id
}

output "load_balancer_dns" {
  description = "LoadBalancer DNS名称"
  value       = aws_lb.app.dns_name
}

output "load_balancer_arn" {
  description = "LoadBalancer ARN"
  value       = aws_lb.app.arn
}

output "load_balancer_zone_id" {
  description = "LoadBalancer hosted zone ID"
  value       = aws_lb.app.zone_id
}

output "sns_alerts_topic_arn" {
  description = "SNS告警主题ARN"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch日志组名称"
  value       = aws_cloudwatch_log_group.app.name
}
