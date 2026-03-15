/**
 * 国际化配置
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang@163.com
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import zh from './zh.json';
import en from './en.json';

// 语言类型
export type Language = 'zh' | 'en';

// 翻译资源
const resources: Record<Language, typeof zh> = {
  zh,
  en,
};

// 创建翻译上下文
interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, any>) => string;
}

const I18nContext = createContext<I18nContextType>({
  language: 'zh',
  setLanguage: () => {},
  t: (key: string) => key,
});

// 翻译函数
function translate(language: Language, key: string, params?: Record<string, any>): string {
  const keys = key.split('.');
  let value: any = resources[language];

  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = (value as Record<string, any>)[k];
    } else {
      return key; // 键不存在时返回原始键
    }
  }

  if (typeof value !== 'string') {
    return key;
  }

  // 替换参数
  if (params) {
    return value.replace(/\{(\w+)\}/g, (_, param) => {
      return params[param] !== undefined ? String(params[param]) : `{${param}}`;
    });
  }

  return value;
}

/**
 * I18n 提供者组件
 */
export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    // 初始化：尝试从localStorage读取语言设置，否则使用浏览器语言
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedLang = localStorage.getItem('drs-language') as Language | null;
      if (savedLang && resources[savedLang]) {
        return savedLang;
      }
    }
    // 检测浏览器语言
    if (typeof navigator !== 'undefined' && navigator.language) {
      const lang = navigator.language.toLowerCase();
      if (lang.startsWith('zh')) {
        return 'zh';
      }
    }
    return 'en';
  });

  const setLanguage = useCallback((lang: Language) => {
    if (resources[lang]) {
      setLanguageState(lang);
      // 持久化语言设置
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('drs-language', lang);
      }
    }
  }, []);

  const t = useCallback((key: string, params?: Record<string, any>) => {
    return translate(language, key, params);
  }, [language]);

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
}

/**
 * React Hook 使用翻译
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { t, language, setLanguage } = useTranslation();
 *   return <div>{t('common.loading')}</div>;
 * }
 * ```
 */
export function useTranslation() {
  return useContext(I18nContext);
}

/**
 * 获取当前语言（不使用 hook）
 */
export function getLanguage(): Language {
  if (typeof window !== 'undefined' && window.localStorage) {
    const savedLang = localStorage.getItem('drs-language') as Language | null;
    if (savedLang && resources[savedLang]) {
      return savedLang;
    }
  }
  return 'zh';
}

/**
 * 持久化语言设置
 */
export function saveLanguagePreference(lang: Language): void {
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem('drs-language', lang);
  }
}

/**
 * 初始化 i18n (不再需要，使用 I18nProvider 替代)
 */
export function initI18n(): void {
  // 空函数，保持向后兼容
}

/**
 * 直接翻译函数（不使用 hook）
 */
export function t(key: string, params?: Record<string, any>): string {
  return translate(getLanguage(), key, params);
}

/**
 * 检测浏览器语言
 */
export function detectBrowserLanguage(): Language {
  if (typeof navigator !== 'undefined' && navigator.language) {
    const lang = navigator.language.toLowerCase();
    if (lang.startsWith('zh')) {
      return 'zh';
    }
  }
  return 'en';
}

// 导出类型
export type Translations = typeof zh;

// 导出所有翻译键（用于类型提示）
export const translationKeys = {
  common: {
    loading: '',
    error: '',
    success: '',
  },
  simulation: {
    title: '',
    create: '',
    start: '',
    pause: '',
    resume: '',
    stop: '',
  },
} as const;
