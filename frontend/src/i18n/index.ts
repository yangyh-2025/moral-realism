/**
 * 国际化配置
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang@163.com
 */

// 由于当前项目未安装i18next，我们提供一个轻量级的国际化解决方案
// 如果需要完整的i18next支持，请先安装依赖：
// npm install i18next react-i18next

import zh from './zh.json';
import en from './en.json';

// 语言类型
export type Language = 'zh' | 'en';

// 当前语言状态
let currentLanguage: Language = 'zh';

// 翻译资源
const resources: Record<Language, typeof zh> = {
  zh,
  en,
};

/**
 * 设置当前语言
 *
 * @param lang - 语言代码
 */
export function setLanguage(lang: Language): void {
  if (resources[lang]) {
    currentLanguage = lang;
  }
}

/**
 * 获取当前语言
 *
 * @returns 当前语言代码
 */
export function getLanguage(): Language {
  return currentLanguage;
}

/**
 * 翻译函数
 *
 * @param key - 翻译键（支持嵌套，如 'common.loading'）
 * @param params - 参数对象
 * @returns 翻译后的文本
 *
 * @example
 * ```tsx
 * t('common.loading') // '加载中...'
 * t('validation.minLength', { min: 3 }) // '最少需要 3 个字符'
 * ```
 */
export function t(key: string, params?: Record<string, any>): string {
  const keys = key.split('.');
  let value: any = resources[currentLanguage];

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
  return {
    t,
    language: currentLanguage,
    setLanguage,
  };
}

// 检测浏览器语言
export function detectBrowserLanguage(): Language {
  if (typeof navigator !== 'undefined' && navigator.language) {
    const lang = navigator.language.toLowerCase();
    if (lang.startsWith('zh')) {
      return 'zh';
    }
  }
  return 'en';
}

// 初始化：尝试从localStorage读取语言设置，否则使用浏览器语言
export function initI18n(): void {
  if (typeof window !== 'undefined' && window.localStorage) {
    const savedLang = localStorage.getItem('drs-language') as Language | null;
    if (savedLang && resources[savedLang]) {
      currentLanguage = savedLang;
    } else {
      currentLanguage = detectBrowserLanguage();
    }
  }
}

// 持久化语言设置
export function saveLanguagePreference(lang: Language): void {
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem('drs-language', lang);
  }
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
