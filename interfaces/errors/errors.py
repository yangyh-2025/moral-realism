"""
自定义错误类

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Optional, Dict, Any


class CustomError(Exception):
    """自定义错误基类"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[Dict] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "status_code": self.status_code,
                "details": self.details
            }
        }


class LLMError(CustomError):
    """LLM相关错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="LLM_ERROR",
            status_code=503,
            details=details
        )


class ValidationError(CustomError):
    """验证错误"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        if details is None:
            details = {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class SimulationError(CustomError):
    """仿真相关错误"""
    def __init__(self, message: str, simulation_id: Optional[str] = None, details: Optional[Dict] = None):
        if details is None:
            details = {}
        if simulation_id:
            details["simulation_id"] = simulation_id
        super().__init__(
            message=message,
            code="SIMULATION_ERROR",
            status_code=400,
            details=details
        )


class StorageError(CustomError):
    """存储相关错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            status_code=500,
            details=details
        )


class NotFoundError(CustomError):
    """资源未找到错误"""
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict] = None):
        if details is None:
            details = {}
        details["resource_type"] = resource_type
        details["resource_id"] = resource_id
        super().__init__(
            message=f"{resource_type} '{resource_id}' not found",
            code="NOT_FOUND",
            status_code=404,
                       details=details
        )


class AuthenticationError(CustomError):
    """认证错误"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(CustomError):
    """授权错误"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class ConfigurationError(CustomError):
    """配置错误"""
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict] = None):
        if details is None:
            details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class TimeoutError(CustomError):
    """超时错误"""
    def __init__(self, message: str = "Operation timeout", operation: Optional[str] = None, details: Optional[Dict] = None):
        if details is None:
            details = {}
        if operation:
            details["operation"] = operation
        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            status_code=408,
            details=details
        )


class RateLimitError(CustomError):
    """速率限制错误"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, details: Optional[Dict] = None):
        if details is None:
            details = {}
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=429,
            details=details
        )
