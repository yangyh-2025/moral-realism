# 道义现实主义社会模拟仿真系统部署脚本 (Windows PowerShell)
#
# Git提交用户名: yangyh-2025
# Git提交邮箱: yangyuhang2667@163.com

# 配置
$IMAGE_NAME = "moral-realism"
$IMAGE_TAG = "latest"

# 函数：打印信息
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

# 函数：检查依赖
function Test-Dependencies {
    Write-Info "检查依赖..."

    try {
        $dockerVersion = docker --version
        Write-Info "Docker 已安装: $dockerVersion"
    } catch {
        Write-Error "Docker 未安装，请先安装 Docker Desktop"
    }

    try {
        $composeVersion = docker-compose --version
        Write-Info "Docker Compose 已安装: $composeVersion"
    } catch {
        Write-Error "Docker Compose 未安装，请先安装 Docker Compose"
    }

    Write-Info "依赖检查通过 ✓"
}

# 函数：检查环境变量
function Test-Environment {
    Write-Info "检查环境变量..."

    if (-not (Test-Path .env)) {
        Write-Warn ".env 文件不存在，请创建并配置必要的环境变量"
        if (Test-Path .env.example) {
            Write-Info "从 .env.example 创建 .env..."
            Copy-Item .env.example .env
        }
    } else {
        Write-Info ".env 文件已存在 ✓"
    }
}

# 函数：创建必要的目录
function New-AppDirectories {
    Write-Info "创建必要的目录..."
    $directories = @("data", "logs", "backups")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
        }
    }
    Write-Info "目录创建完成 ✓"
}

# 函数：构建 Docker 镜像
function Build-DockerImages {
    Write-Info "构建 Docker 镜像..."
    docker-compose build --no-cache
    Write-Info "镜像构建完成 ✓"
}

# 函数：启动服务
function Start-Services {
    Write-Info "启动服务..."
    docker-compose up -d

    Write-Info "等待服务启动..."
    Start-Sleep -Seconds 10

    docker-compose ps

    Write-Info "服务启动完成 ✓"
}

# 函数：停止服务
function Stop-Services {
    Write-Info "停止服务..."
    docker-compose down
    Write-Info "服务已停止 ✓"
}

# 函数：重启服务
function Restart-Services {
    Write-Info "重启服务..."
    docker-compose restart
    Write-Info "服务已重启 ✓"
}

# 函数：查看日志
function Show-Logs {
    param([string]$Service = "")

    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

# 函数：健康检查
function Test-Health {
    Write-Info "执行健康检查..."

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        Write-Info "后端服务健康 ✓"
    } catch {
        Write-Error "后端服务不健康: $_"
    }

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Info "前端服务健康 ✓"
    } catch {
        Write-Error "前端服务不健康: $_"
    }
}

# 函数：清理
function Remove-Cleanup {
    Write-Info "清理资源..."

    $confirmation = Read-Host "确定要删除所有容器和镜像吗？(y/N)"
    if ($confirmation -eq "y" -or $confirmation -eq "Y") {
        docker-compose down --rmi all -v
        Write-Info "清理完成 ✓"
    } else {
        Write-Info "取消清理"
    }
}

# 函数：显示帮助
function Show-Help {
    Write-Host "道义现实主义社会模拟仿真系统部署脚本 (Windows)"
    Write-Host ""
    Write-Host "用法: .\deploy.ps1 [命令]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  build       构建 Docker 镜像"
    Write-Host "  start       启动服务"
    Write-Host "  stop        停止服务"
    Write-Host "  restart     重启服务"
    Write-Host "  logs [服务] 查看日志（可选指定服务名）"
    Write-Host "  health      健康检查"
    Write-Host "  cleanup     清理所有容器和镜像"
    Write-Host "  deploy      完整部署（build + start）"
    Write-Host "  dev         开发模式部署"
    Write-Host "  help        显示帮助信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\deploy.ps1 deploy"
    Write-Host "  .\deploy.ps1 logs backend"
    Write-Host "  .\deploy.ps1 health"
}

# 主函数
function Main {
    param([string]$Command = "help")

    switch ($Command) {
        "build" {
            Test-Dependencies
            New-AppDirectories
            Build-DockerImages
        }
        "start" {
            Test-Dependencies
            Test-Environment
            New-AppDirectories
            Start-Services
            Test-Health
            Write-Host ""
            Write-Info "访问地址:"
            Write-Info "  前端: http://localhost:3000"
            Write-Info "  后端 API: http://localhost:8000/api/docs"
            Write-Info "  后端健康: http://localhost:8000/health"
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "logs" {
            $service = $args[1]
            Show-Logs $service
        }
        "health" {
            Test-Health
        }
        "cleanup" {
            Remove-Cleanup
        }
        "deploy" {
            Test-Dependencies
            Test-Environment
            New-AppDirectories
            Build-DockerImages
            Start-Services
            Test-Health
            Write-Host ""
            Write-Info "部署完成！"
            Write-Info "访问地址:"
            Write-Info "  前端: http://localhost:3000"
            Write-Info "  后端 API: http://localhost:8000/api/docs"
        }
        "dev" {
            Test-Dependencies
            Test-Environment
            New-AppDirectories
            Write-Info "启动开发环境..."
            docker-compose -f docker-compose.dev.yml up -d
            Write-Info "开发环境启动完成 ✓"
        }
        "help" {
            Show-Help
        }
        default {
            Show-Help
        }
    }
}

# 执行主函数
Main @args
