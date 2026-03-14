/**
 * 应用入口
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ToastContainer from './components/ui/notifications/ToastContainer';
import './index.css';
import './styles/tokens.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <ToastContainer />
  </React.StrictMode>
);
