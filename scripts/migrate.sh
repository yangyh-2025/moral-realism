#!/bin/bash
# 数据库迁移脚本
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

set -e

echo "========================================="
echo "数据库迁移脚本"
echo "========================================="
echo "开始数据库迁移..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查alembic是否安装
if ! python -c "import alembic" 2>/dev/null; then
    echo "错误: alembic未安装"
    echo "请运行: pip install alembic"
    exit 1
fi

# 检查alembic.ini是否存在
if [ ! -f "alembic.ini" ]; then
    echo "警告: alembic.ini不存在，尝试初始化alembic..."
    echo "运行: alembic init migrations"
    alembic init migrations
    echo "请配置alembic.ini中的数据库连接字符串"
    echo "然后重新运行迁移脚本"
    exit 1
fi

# 检查migrations目录是否存在
if [ ! -d "migrations" ]; then
    echo "错误: migrations目录不存在"
    echo "请运行: alembic init migrations"
    exit 1
fi

# 显示当前迁移版本
echo ""
echo "当前迁移状态:"
alembic current 2>/dev/null || echo "无法获取当前版本"

# 运行迁移
echo ""
echo "正在运行迁移到最新版本..."
alembic upgrade head

# 检查迁移是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "迁移成功！"
    echo "========================================="
    echo "最新迁移版本:"
    alembic current
else
    echo ""
    echo "========================================="
    echo "迁移失败！"
    echo "========================================="
    exit 1
fi
