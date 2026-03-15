/**
 * 应用入口

 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// 从 localStorage 加载设置并立即应用
const savedSettings = localStorage.getItem('systemSettings');
if (savedSettings) {
  try {
    const settings = JSON.parse(savedSettings);
    // 应用主题
    if (settings.theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      document.documentElement.classList.remove('dark');
    }
    // 应用强调色
    if (settings.accentColor) {
      document.documentElement.style.setProperty('--color-accent', settings.accentColor);
    }
  } catch (error) {
    console.error('Failed to load settings on startup:', error);
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
