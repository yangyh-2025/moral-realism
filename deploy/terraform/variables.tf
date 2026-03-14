# Terraform变量定义
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

variable "aws_region" {
  description = "AWS区域"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "环境名称 (dev/staging/prod)"
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment必须是 dev, staging 或 prod"
  }
}

variable "kubernetes_version" {
  description = "Kubernetes版本"
  type        = string
  default     = "1.28"
}

variable "vpc_cidr" {
  description = "VPC CIDR块"
  type        = string
  default     = "10.0.0.0/16"
}

variable "node_min_size" {
  description = "EKS节点组最小节点数"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "EKS节点组最大节点数"
  type        = number
  default     = 10
}

variable "node_desired_size" {
  description = "EKS节点组期望节点数"
  type        = number
  default     = 3
}

variable "db_username" {
  description = "数据库用户名"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}

variable "acm_certificate_arn" {
  description = "AWS Certificate Manager证书ARN"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "是否启用监控"
  type        = bool
  default     = true
}

variable "enable_autoscaling" {
  description = "是否启用自动扩缩容"
  type        = bool
  default     = true
}
