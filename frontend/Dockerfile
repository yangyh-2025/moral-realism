# 前端 Dockerfile - 多阶段构建

# 阶段 1: 依赖安装
FROM node:18-alpine AS deps

WORKDIR /app

# 复制 package 文件
COPY package.json package-lock.json ./

# 安装依赖
RUN npm ci --only=production

# 阶段 2: 构建
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 构建应用
RUN npm run build

# 阶段 3: 生产运行
FROM nginx:alpine AS production

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
