/**
 * 主应用组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={<div>仪表板页面（待实现）</div>}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
