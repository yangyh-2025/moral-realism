# Terraform配置文件
# 用于部署ABM仿真系统到云基础设施
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

# Provider配置
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~>2.23.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11.0"
    }
  }

  backend "s3" {
    bucket         = "abm-simulation-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "abm-simulation-terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ABM-Simulation"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name,
      "--region",
      var.aws_region
    ]
  }
}

# 获取当前AWS账户信息
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ============================================
# VPC网络配置
# ============================================

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "abm-simulation-${var.environment}"
  cidr = var.vpc_cidr

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = [cidrsubnet(var.vpc_cidr, 3, 1), cidrsubnet(var.vpc_cidr, 3, 2), cidrsubnet(var.vpc_cidr, 3, 3)]
  public_subnets  = [cidrsubnet(var.vpc_cidr, 3, 0), cidrsubnet(var.vpc_cidr, 3, 4), cidrsubnet(var.vpc_cidr, 3, 5)]

  enable_nat_gateway     = true
  single_nat_gateway      = true
  enable_dns_hostnames    = true
  enable_dns_support      = true

  tags = {
    Name = "abm-simulation-${var.environment}"
  }
}

# ============================================
# EKS Kubernetes集群配置
# ============================================

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "abm-simulation-${var.environment}"
  cluster_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  eks_managed_node_groups = {
    primary = {
      name           = "abm-simulation-nodes"
      instance_types = ["t3.large"]
      min_size       = var.node_min_size
      max_size       = var.node_max_size
      desired_size   = var.node_desired_size

      labels = {
        Environment = var.environment
        Project     = "ABM-Simulation"
      }
    }
  }

  tags = {
    Name = "abm-simulation-${var.environment}"
  }
}

# ============================================
# ECR容器注册表
# ============================================

resource "aws_ecr_repository" "app" {
  name                 = "abm-simulation-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "abm-simulation-app"
  }
}

# ============================================
# RDS PostgreSQL数据库
# ============================================

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "abm-simulation-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class      = "db.t3.medium"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = "abm_simulation"
  username = var.db_username
  password = var.db_password

  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.rds.id]

  monitoring_interval    = 60
  performance_insights_enabled = true

  tags = {
    Name = "abm-simulation-db"
  }
}

# RDS安全组
resource "aws_security_group" "rds" {
  name_prefix = "abm-simulation-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  tags = {
    Name = "abm-simulation-rds-sg"
  }
}

# ============================================
# S3存储桶 (备份和日志)
# ============================================

resource "aws_s3_bucket" "backups" {
  bucket = "abm-simulation-backups-${var.environment}"

  tags = {
    Name = "abm-simulation-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "delete-old-backups"
    status = "Enabled"

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "abm-simulation-logs-${var.environment}"

  tags = {
    Name = "abm-simulation-logs"
  }
}

# ============================================
# Terraform状态管理
# ============================================

resource "aws_s3_bucket" "terraform_state" {
  bucket = "abm-simulation-terraform-state"

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_dynamodb_table" "terraform_lock" {
  name         = "abm-simulation-terraform-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "abm-simulation-terraform-lock"
  }
}

# ============================================
# CloudWatch日志组和告警
# ============================================

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/eks/abm-simulation-${var.environment}/application"
  retention_in_days = 30

  tags = {
    Name = "abm-simulation-app-logs"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "abm-simulation-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "cpu_usage_average"
  namespace           = "AWS/EKS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"

  dimensions = {
    ClusterName = module.eks.cluster_name
  }

  alarm_actions          = [aws_sns_topic.alerts.arn]
  insufficient_data_actions = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "abm-simulation-high-cpu-alarm"
  }
}

resource "aws_sns_topic" "alerts" {
  name = "abm-simulation-alerts-${var.environment}"

  tags = {
    Name = "abm-simulation-alerts"
  }
}

# ============================================
# 额外资源: LoadBalancer
# ============================================

resource "aws_lb" "app" {
  name               = "abm-simulation-lb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = false

  tags = {
    Name = "abm-simulation-load-balancer"
  }
}

resource "aws_security_group" "lb" {
  name_prefix = "abm-simulation-lb-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "abm-simulation-lb-sg"
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_lb_target_group" "app" {
  name        = "abm-simulation-tg-${var.environment}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/api/docs"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name = "abm-simulation-target-group"
  }
}

# ============================================
# Helm Release: NGINX Ingress Controller
# ============================================

resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"
  create_namespace = true

  set {
    name  = "controller.replicaCount"
    value = "2"
  }

  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
    value = "nlb"
  }

  depends_on = [module.eks]
}
