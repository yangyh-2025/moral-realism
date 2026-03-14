#!/bin/bash
# 道义现实主义社会模拟仿真系统部署脚本
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
IMAGE_NAME="moral-realism"
IMAGE_TAG="latest"
REGISTRY=""  # 留空表示本地仓库

# 函数：打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 函数：检查依赖
check_dependencies() {
    info "检查依赖..."

    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose 未安装，请先安装 Docker Compose"
    fi

    info "依赖检查通过 ✓"
}

# 函数：检查环境变量
check_env() {
    info "检查环境变量..."

    if [ ! -f .env ]; then
        warn ".env 文件不存在，从示例创建..."
        if [ -f .env.example ]; then
            cp .env.example .env
            info "已创建 .env 文件，请配置 LLM_API_KEY"
        else
            warn "请创建 .env 文件并配置必要的环境变量"
        fi
    else
        info ".env 文件已存在 ✓"
    fi

    # 检查必需的环境变量
    source .env
    if [ -z "$MORAL_REALISM_LLM_API_KEY" ]; then
        warn "警告: MORAL_REALISM_LLM_API_KEY 未设置"
    fi
}

# 函数：创建必要的目录
create_directories() {
    info "创建必要的目录..."
    mkdir -p data logs backups
    info "目录创建完成 ✓"
}

# 函数：构建 Docker 镜像
build_images() {
    info "构建 Docker 镜像..."

    docker-compose build --no-cache

    info "镜像构建完成 ✓"
}

# 函数：启动服务
start_services() {
    info "启动服务..."

    docker-compose up -d

    info "等待服务启动..."
    sleep 10

    # 检查服务状态
    docker-compose ps

    info "服务启动完成 ✓"
}

# 函数：停止服务
stop_services() {
    info "停止服务..."
    docker-compose down
    info "服务已停止 ✓"
}

# 函数：重启服务
restart_services() {
    info "重启服务..."
    docker-compose restart
    info "服务已重启 ✓"
}

# 函数：查看日志
view_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# 函数：健康检查
health_check() {
    info "执行健康检查..."

    # 检查后端
    if curl -f http://localhost:8000/health &> /dev/null; then
        info "后端服务健康 ✓"
    else
        error "后端服务不健康"
    fi

    # 检查前端
    if curl -f http://localhost:3000 &> /dev/null; then
        info "前端服务健康 ✓"
    else
        error "前端服务不健康"
    fi
}

# 函数：清理
cleanup() {
    info "清理资源..."

    read -p "确定要删除所有容器和镜像吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --rmi all -v
        info "清理完成 ✓"
    else
        info "取消清理"
    fi
}

# 函数：显示帮助
show_help() {
    echo "道义现实主义社会模拟仿真系统部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build       构建 Docker 镜像"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  logs [服务] 查看日志（可选指定服务名）"
    echo "  health      健康检查"
    echo "  cleanup     清理所有容器和镜像"
    echo "  deploy      完整部署（build + start）"
    echo "  dev         开发模式部署"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy"
    echo "  $0 logs backend"
    echo "  $0 health"
}

# 主函数
main() {
    local command=${1:-help}

    case $command in
        build)
            check_dependencies
            create_directories
            build_images
            ;;
        start)
            check_dependencies
            check_env
            create_directories
            start_services
            health_check
            info ""
            info "访问地址:"
            info "  前端: http://localhost:3000"
            info "  后端 API: http://localhost:8000/api/docs"
            info "  后端健康: http://localhost:8000/health"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            view_logs "$2"
            ;;
        health)
            health_check
            ;;
        cleanup)
            cleanup
            ;;
        deploy)
            check_dependencies
            check_env
            create_directories
            build_images
            start_services
            health_check
            info ""
            info "部署完成！"
            info "访问地址:"
            info "  前端: http://localhost:3000"
            info "  后端 API: http://localhost:8000/api/docs"
            ;;
        dev)
            check_dependencies
            check_env
            create_directories
            info "启动开发环境..."
            docker-compose -f docker-compose.dev.yml up -d
            info "开发环境启动完成 ✓"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
