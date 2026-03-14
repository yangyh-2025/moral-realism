/**
 * 错误边界组件
 *
 * 用于捕获React组件树错误并显示友好的错误信息
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * 错误边界组件
 *
 * 用法：
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by ErrorBoundary:', error, errorInfo);

    this.setState({ errorInfo });

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-lg w-full bg-white rounded-xl shadow-lg p-8">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 mb-2">出错了</h2>
              <p className="text-gray-600 mb-6">应用程序遇到了一个意外错误</p>

              {this.state.error && {
                <div className="bg-red-50 border border-error-light rounded-lg p-4 mb-6">
                  <p className="text-sm font-medium text-error-dark mb-2">{this.state.error.message}</p>
                  {process.env.NODE_ENV === 'development' && this.state.error.stack && {
                    <details className="mt-2">
                      <summary className="text-xs text-error cursor-pointer hover:text-error-dark">查看堆栈跟踪</summary>
                      <pre className="mt-2 text-xs text-error-dark overflow-auto max-h-40 bg-red-100 p-2 rounded">
                        {this.state.error.stack}
                      </pre>
                    </details>
                  }}
                </div>
              }}

              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleReset}
                  className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent-hover transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
                >
                  重新加载
                </button>
                <button
                  onClick={() => window.location.href = '/'}
                  className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
                >
                  返回首页
                </button>
              </div>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.errorInfo && {
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-500 mb-2">组件堆栈：</p>
                <pre className="text-xs text-gray-600 overflow-auto max-h-40 bg-gray-50 p-3 rounded">
                  {this.state.errorInfo.componentStack}
                </pre>
              </div>
            }}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
