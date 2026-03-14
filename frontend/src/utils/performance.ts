/**
 * 性能优化工具
 *
 * 提供组件加载时间追踪、防抖节流函数、内存使用等功能
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang@163.com
 */

/**
 * 组件加载时间追踪
 *
 * @param componentName - 组件名称
 * @returns 返回一个函数，调用时记录加载时间
 *
 * @example
 * ```tsx
 * useEffect(() => {
 *   const trackLoad = trackComponentLoad('MyComponent');
 *   // ... 组件初始化代码
 *   trackLoad();
 * }, []);
 * ```
 */
export function trackComponentLoad(componentName: string): () => void {
  const startTime = performance.now();

  return () => {
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.log(`[Performance] ${componentName} loaded in ${duration.toFixed(2)}ms`);

    // 发送到Google Analytics
    if ((window as any).gtag) {
      (window as any).gtag('event', 'component_load', {
        event_category: 'Performance',
        event_action: 'component_load',
        event_label: componentName,
        value: Math.round(duration),
        custom_map: { metric_duration: duration },
      });
    }
  };
}

/**
 * 防抖函数
 *
 * 在指定时间内多次调用只执行最后一次
 *
 * @param func - 要执行的函数
 * @param wait - 等待时间（毫秒）
 * @returns 防抖后的函数
 *
 * @example
 * ```tsx
 * const debouncedSearch = debounce((query: string) => {
 *   // 执行搜索
 * }, 300);
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * 节流函数
 *
 * 在指定时间内多次调用只执行第一次
 *
 * @param func - 要执行的函数
 * @param limit - 限制时间（毫秒）
 * @returns 节流后的函数
 *
 * @example
 * ```tsx
 * const throttledScroll = throttle(() => {
 *   // 处理滚动事件
 * }, 100);
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;
  let lastArgs: Parameters<T> | null = null;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
        if (lastArgs) {
          func(...lastArgs);
          lastArgs = null;
        }
      }, limit);
    } else {
      lastArgs = args;
    }
  };
}

/**
 * 内存使用监控
 *
 * 记录当前内存使用情况（仅Chrome可用）
 */
export function monitorMemoryUsage(): { used: number; total: number; limit: number } | null {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    const used = Math.round(memory.usedJSHeapSize / 1048576);
    const total = Math.round(memory.totalJSHeapSize / 1048576);
    const limit = Math.round(memory.jsHeapSizeLimit / 1048576);

    console.log(`[Memory] Used: ${used}MB / Total: ${total}MB / Limit: ${limit}MB`);

    return { used, total, limit };
  }
  return null;
}

/**
 * 开始性能标记
 *
 * @param name - 标记名称
 */
export function startPerformanceMark(name: string): void {
  try {
    performance.mark(`${name}-start`);
  } catch (error) {
    console.warn('Failed to start performance mark:', error);
  }
}

/**
 * 结束性能标记并测量
 *
 * @param name - 标记名称
 * @returns 持续时间（毫秒），如果失败返回null
 */
export function endPerformanceMark(name: string): number | null {
  try {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);

    const measure = performance.getEntriesByName(name)[0];
    const duration = measure ? measure.duration : null;

    // 清除标记和测量
    performance.clearMarks(`${name}-start`);
    performance.clearMarks(`${name}-end`);
    performance.clearMeasures(name);

    if (duration !== null) {
      console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    }

    return duration;
  } catch (error) {
    console.warn('Failed to end performance mark:', error);
    return null;
  }
}

/**
 * 请求空闲回调
 *
 * 在浏览器空闲时执行任务
 *
 * @param callback - 要执行的回调函数
 * @param options - 选项
 */
export function requestIdleCallback(
  callback: () => void,
  options?: { timeout?: number }
): void {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    (window as any).requestIdleCallback(callback, options);
  } else {
    // 回退到setTimeout
    setTimeout(callback, options?.timeout || 0);
  }
}

/**
 * 批量执行任务
 *
 * 将任务分成多个时间段执行，避免阻塞主线程
 *
 * @param tasks - 任务数组
 * @param batchSize - 每批次任务数量
 * @param delay - 批次间延迟（毫秒）
 */
export async function batchExecute<T, R>(
  tasks: Array<() => Promise<R> | R>,
  batchSize: number = 10,
  delay: number = 50
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < tasks.length; i += batchSize) {
    const batch = tasks.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(task => Promise.resolve(task()))
    );
    results.push(...batchResults);

    // 等待一帧后再继续
    if (i + batchSize < tasks.length) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return results;
}

/**
 * 资源加载性能监控
 *
 * @returns 资源性能数据
 */
export function getResourcePerformance(): PerformanceResourceTiming[] {
  if (typeof performance === 'undefined' || !performance.getEntriesByType) {
    return [];
  }
  return performance.getEntriesByType('resource') as PerformanceResourceTiming[];
}

/**
 * 页面加载性能数据
 *
 * @returns 页面性能数据
 */
export function getPageLoadPerformance(): {
  domContentLoaded: number | null;
  loadComplete: number | null;
  firstPaint: number | null;
  firstContentfulPaint: number | null;
} {
  if (typeof performance === 'undefined' || !performance.getEntriesByType) {
    return {
      domContentLoaded: null,
      loadComplete: null,
      firstPaint: null,
      firstContentfulPaint: null,
    };
  }

  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
  const paint = performance.getEntriesByType('paint');

  return {
    domContentLoaded: navigation?.domContentLoadedEventEnd
      ? Math.round(navigation.domContentLoadedEventEnd)
      : null,
    loadComplete: navigation?.loadEventEnd ? Math.round(navigation.loadEventEnd) : null,
    firstPaint: paint.find((p: any) => p.name === 'first-paint')?.startTime ?? null,
    firstContentfulPaint: paint.find((p: any) => p.name === 'first-contentful-paint')?.startTime ?? null,
  };
}

/**
 * 生成性能报告
 *
 * @returns 性能报告对象
 */
export function generatePerformanceReport(): {
  timestamp: number;
  memory: ReturnType<typeof monitorMemoryUsage>;
  pageLoad: ReturnType<typeof getPageLoadPerformance>;
  resources: number;
} {
  return {
    timestamp: Date.now(),
    memory: monitorMemoryUsage(),
    pageLoad: getPageLoadPerformance(),
    resources: getResourcePerformance().length,
  };
}
