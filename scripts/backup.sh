#!/bin/bash
# 数据库备份脚本
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

set -e

# 配置
BACKUP_DIR="backups"
DATA_DIR="data"
DATABASE_FILE="database.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.db"
RETENTION_DAYS=7

echo "========================================="
echo "数据库备份脚本"
echo "========================================="
echo "开始备份..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查数据库文件是否存在
if [ ! -f "$DATA_DIR/$DATABASE_FILE" ]; then
    echo "错误: 数据库文件不存在: $DATA_DIR/$DATABASE_FILE"
    exit 1
fi

# 创建备份目录
mkdir -p $BACKUP_DIR

# 复制数据库文件
echo "正在复制数据库文件..."
cp "$DATA_DIR/$DATABASE_FILE" "$BACKUP_FILE"

# 检查复制是否成功
if [ $? -eq 0 ]; then
    echo "数据库文件复制成功"
else
    echo "错误: 数据库文件复制失败"
    exit 1
fi

# 获取文件大小
FILE_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "unknown")
echo "备份文件大小: $FILE_SIZE bytes"

# 压缩备份
echo "正在压缩备份文件..."
gzip "$BACKUP_FILE"

# 检查压缩是否成功
if [ $? -eq 0 ]; then
    echo "压缩成功: $BACKUP_FILE.gz"
else
    echo "警告: 压缩失败，保留未压缩文件"
fi

# 清理旧备份
echo ""
echo "清理超过 $RETENTION_DAYS 天的旧备份..."
DELETED_COUNT=$(find $BACKUP_DIR -name "backup_*.db.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
echo "已删除 $DELETED_COUNT 个旧备份文件"

# 显示备份统计
echo ""
echo "========================================="
echo "备份统计"
echo "========================================="
BACKUP_COUNT=$(find $BACKUP_DIR -name "backup_*.db*" | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1 || echo "unknown")
echo "当前备份总数: $BACKUP_COUNT"
echo "备份目录总大小: $TOTAL_SIZE"

echo ""
echo "备份完成！"
echo "备份文件: ${BACKUP_FILE}.gz"
echo "========================================="
