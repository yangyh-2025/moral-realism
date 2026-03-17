/**
 * 系统设置页面
 *
 * 功能：
 * 1. API配置管理
 * 2. 仿真参数设置
 * 3. 主题选择功能
 * 4. 语言选择功能
 * 5. 设置持久化
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import { addNotification, setTheme } from '../store/slices/uiSlice';
import { useTranslation } from '../i18n';
import type { Language } from '../i18n';
import { Card } from '../components/ui/cards/Card';
import { CardBody } from '../components/ui/cards/CardBody';
import { CardHeader } from '../components/ui/cards/CardHeader';
import { Input } from '../components/ui/form/Input';
import { Textarea } from '../components/ui/form/Textarea';
import { Select } from '../components/ui/form/Select';
import { Button } from '../components/ui/buttons/Button';
import { Alert } from '../components/ui/feedback/Alert';
import { Badge } from '../components/ui/data/Badge';
import { SaveIcon, RefreshIcon } from '../components/ui/icons';

interface SystemSettings {
  // API配置
  apiBaseUrl: string;
  apiTimeout: number;
  websocketUrl: string;

  // 仿真参数默认值
  defaultTotalRounds: number;
  defaultRoundDuration: number;
  defaultRandomEventProb: number;
  defaultCheckpointInterval: number;

  // 主题设置
  theme: 'light' | 'dark' | 'auto';
  accentColor: string;

  // 显示设置
  language: 'zh-CN' | 'en-US';
  autoRefresh: boolean;
  refreshInterval: number;

  // 数据设置
  autoSave: boolean;
  maxHistory: number;
}

export const SystemSettings: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { t, language: i18nLanguage, setLanguage } = useTranslation();

  const [settings, setSettings] = useState<SystemSettings>({
    apiBaseUrl: 'http://localhost:8000',
    apiTimeout: 30000,
    websocketUrl: 'ws://localhost:8000/ws',
    defaultTotalRounds: 100,
    defaultRoundDuration: 6,
    defaultRandomEventProb: 0.1,
    defaultCheckpointInterval: 10,
    theme: 'light',
    accentColor: '#3B82F6',
    language: 'zh-CN',
    autoRefresh: true,
    refreshInterval: 2000,
    autoSave: true,
    maxHistory: 100,
  });

  const [activeTab, setActiveTab] = useState<'api' | 'simulation' | 'display' | 'data'>('api');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('systemSettings');
      if (saved) {
        const parsedSettings = JSON.parse(saved);
        setSettings(parsedSettings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  // 安全的 JSON 字符串化函数，处理循环引用
  const safeStringify = (obj: any, space?: number): string => {
    const seen = new WeakSet();
    return JSON.stringify(obj, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (seen.has(value)) {
          return '[Circular]';
        }
        seen.add(value);
      }
      return value;
    }, space);
  };

  const saveSettings = async () => {
    setIsSaving(true);
    console.log('正在保存设置...', settings);
    try {
      const settingsJson = safeStringify(settings);
      console.log('Settings JSON:', settingsJson);
      localStorage.setItem('systemSettings', settingsJson);
      console.log('已保存到 localStorage');

      // 应用主题设置到 Redux store
      if (settings.theme === 'light' || settings.theme === 'dark') {
        dispatch(setTheme(settings.theme));
      }

      // 应用强调色到 CSS 变量
      document.documentElement.style.setProperty('--color-accent', settings.accentColor);

      // 应用语言设置到 i18n
      const langCode = settings.language === 'zh-CN' ? 'zh' : 'en';
      setLanguage(langCode);

      setHasUnsavedChanges(false);
      dispatch(addNotification({
        type: 'success',
        title: t('common.success'),
        message: t('settings.saved'),
      }));
    } catch (error) {
      console.error('保存设置失败:', error);
      dispatch(addNotification({
        type: 'error',
        title: t('common.error'),
        message: `${t('settings.saveFailed')}: ${error instanceof Error ? error.message : t('common.error')}`,
      }));
    } finally {
      setIsSaving(false);
    }
  };

  const resetSettings = () => {
    if (!confirm(t('settings.resetConfirm'))) return;

    const defaultSettings: SystemSettings = {
      apiBaseUrl: 'http://localhost:8000',
      apiTimeout: 30000,
      websocketUrl: 'ws://localhost:8000/ws',
      defaultTotalRounds: 100,
      defaultRoundDuration: 6,
      defaultRandomEventProb: 0.1,
      defaultCheckpointInterval: 10,
      theme: 'light',
      accentColor: '#3B82F6',
      language: i18nLanguage === 'zh' ? 'zh-CN' : 'en-US',
      autoRefresh: true,
      refreshInterval: 2000,
      autoSave: true,
      maxHistory: 100,
    };

    setSettings(defaultSettings);
    setHasUnsavedChanges(true);
  };

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    console.log('Setting change:', key, 'value:', value, 'type:', typeof value);
    setSettings({ ...settings, [key]: value });
    setHasUnsavedChanges(true);
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${settings.apiBaseUrl}/health`);
      if (response.ok) {
        dispatch(addNotification({
          type: 'success',
          title: t('settings.connectionSuccess'),
          message: t('settings.connectionSuccessMessage'),
        }));
      } else {
        throw new Error('Server returned error');
      }
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: t('settings.connectionFailed'),
        message: t('settings.connectionFailedMessage'),
      }));
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('settings.title')}</h1>
          <p className="text-sm text-gray-600 mt-1">
            {t('settings.description')}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            onClick={resetSettings}
          >
            {t('settings.reset')}
          </Button>
          <Button
            variant="primary"
            onClick={saveSettings}
            loading={isSaving}
            leftIcon={<SaveIcon size={16} />}
            disabled={!hasUnsavedChanges}
          >
            {t('settings.save')}
          </Button>
        </div>
      </div>

      {/* 未保存提示 */}
      {hasUnsavedChanges && (
        <Alert variant="warning" title={t('settings.unsavedChanges')}>
          {t('settings.unsavedChangesMessage')}
        </Alert>
      )}

      {/* 标签页导航 */}
      <div className="flex gap-2 border-b border-gray-200">
        <TabButton
          active={activeTab === 'api'}
          label={t('settings.apiConfig')}
          onClick={() => setActiveTab('api')}
        />
        <TabButton
          active={activeTab === 'simulation'}
          label={t('settings.simulationParams')}
          onClick={() => setActiveTab('simulation')}
        />
        <TabButton
          active={activeTab === 'display'}
          label={t('settings.displaySettings')}
          onClick={() => setActiveTab('display')}
        />
        <TabButton
          active={activeTab === 'data'}
          label={t('settings.dataSettings')}
          onClick={() => setActiveTab('data')}
        />
      </div>

      {/* 设置内容 */}
      {activeTab === 'api' && (
        <ApiSettings
          settings={settings}
          onChange={handleSettingChange}
          onTestConnection={testConnection}
        />
      )}

      {activeTab === 'simulation' && (
        <SimulationSettings
          settings={settings}
          onChange={handleSettingChange}
        />
      )}

      {activeTab === 'display' && (
        <DisplaySettings
          settings={settings}
          onChange={handleSettingChange}
        />
      )}

      {activeTab === 'data' && (
        <DataSettings
          settings={settings}
          onChange={handleSettingChange}
        />
      )}
    </div>
  );
};

// 标签页按钮组件
const TabButton: React.FC<{
  active: boolean;
  label: string;
  onClick: () => void;
}> = ({
  active, label, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium transition-colors border-b-2 ${
        active
          ? 'border-accent text-accent'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`}
    >
      {label}
    </button>
  );
};

// API配置组件
const ApiSettings: React.FC<{
  settings: SystemSettings;
  onChange: (key: keyof SystemSettings, value: any) => void;
  onTestConnection: () => void;
}> = ({ settings, onChange, onTestConnection }) => {
  const { t } = useTranslation();
  return (
    <Card>
      <CardHeader
        title={t('settings.apiConfig')}
        subtitle={t('settings.apiConfigDesc')}
      />
      <CardBody>
        <div className="space-y-4">
          <Input
            label={t('settings.apiBaseUrl')}
            value={settings.apiBaseUrl}
            onChange={(e) => onChange('apiBaseUrl', e.target.value)}
            placeholder="http://localhost:8000"
            fullWidth
          />

          <Input
            type="number"
            label={t('settings.apiTimeout')}
            value={settings.apiTimeout}
            onChange={(e) => onChange('apiTimeout', parseInt(e.target.value))}
            min={1000}
            max={300000}
            fullWidth
          />

          <Input
            label={t('settings.websocketUrl')}
            value={settings.websocketUrl}
            onChange={(e) => onChange('websocketUrl', e.target.value)}
            placeholder="ws://localhost:8000/ws"
            fullWidth
          />

          <div className="flex justify-end">
            <Button
              variant="secondary"
              onClick={onTestConnection}
              leftIcon={<RefreshIcon size={14} />}
            >
              {t('settings.testConnection')}
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

// 仿真参数组件
const SimulationSettings: React.FC<{
  settings: SystemSettings;
  onChange: (key: keyof SystemSettings, value: any) => void;
}> = ({ settings, onChange }) => {
  const { t } = useTranslation();
  return (
    <Card>
      <CardHeader
        title={t('settings.simulationParams')}
        subtitle={t('settings.simulationParamsDesc')}
      />
      <CardBody>
        <div className="space-y-4">
          <Input
            type="number"
            label={t('settings.defaultTotalRounds')}
            value={settings.defaultTotalRounds}
            onChange={(e) => onChange('defaultTotalRounds', parseInt(e.target.value))}
            min={1}
            max={1000}
            fullWidth
          />

          <Input
            type="number"
            label={t('settings.defaultRoundDuration')}
            value={settings.defaultRoundDuration}
            onChange={(e) => onChange('defaultRoundDuration', parseInt(e.target.value))}
            min={1}
            max={12}
            fullWidth
          />

          <Input
            type="number"
            label={t('settings.defaultRandomEventProb')}
            value={settings.defaultRandomEventProb}
            onChange={(e) => onChange('defaultRandomEventProb', parseFloat(e.target.value))}
            min={0}
            max={1}
            step={0.01}
            fullWidth
          />

          <Input
            type="number"
            label={t('settings.defaultCheckpointInterval')}
            value={settings.defaultCheckpointInterval}
            onChange={(e) => onChange('defaultCheckpointInterval', parseInt(e.target.value))}
            min={1}
            fullWidth
          />
        </div>
      </CardBody>
    </Card>
  );
};

// 显示设置组件
// 开关组件
const Toggle: React.FC<{
  checked: boolean;
  onChange: (checked: boolean) => void;
}> = ({ checked, onChange }) => {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`relative w-12 h-6 rounded-full transition-colors ${
        checked ? 'bg-accent' : 'bg-gray-300'
      }`}
    >
      <div
        className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
          checked ? 'left-7' : 'left-1'
        }`}
      />
    </button>
  );
};

const DisplaySettings: React.FC<{
  settings: SystemSettings;
  onChange: (key: keyof SystemSettings, value: any) => void;
}> = ({ settings, onChange }) => {
  const { t } = useTranslation();

  const themes = [
    { value: 'light', label: t('settings.themeLight') },
    { value: 'dark', label: t('settings.themeDark') },
    { value: 'auto', label: t('settings.themeAuto') },
  ];

  const languages = [
    { value: 'zh-CN', label: t('settings.languageZhCN') },
    { value: 'en-US', label: t('settings.languageEnUS') },
  ];

  const accentColors = [
    { value: '#3B82F6', label: t('settings.accentBlue'), color: '#3B82F6' },
    { value: '#10B981', label: t('settings.accentGreen'), color: '#10B981' },
    { value: '#F59E0B', label: t('settings.accentOrange'), color: '#F59E0B' },
    { value: '#EF4444', label: t('settings.accentRed'), color: '#EF4444' },
    { value: '#8B5CF6', label: t('settings.accentPurple'), color: '#8B5CF6' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader title={t('settings.theme')} />
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('settings.theme')}
              </label>
              <Select
                value={settings.theme}
                onChange={(value) => onChange('theme', value)}
                options={themes}
                fullWidth
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('settings.accentColor')}
              </label>
              <div className="flex flex-wrap gap-2">
                {accentColors.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => onChange('accentColor', color.value)}
                    className={`w-10 h-10 rounded-full transition-transform ${
                      settings.accentColor === color.value
                        ? 'ring-2 ring-offset-2 ring-gray-400 scale-110'
                        : ''
                    }`}
                    style={{ backgroundColor: color.color }}
                    title={color.label}
                  />
                ))}
              </div>
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title={t('settings.language')} />
        <CardBody>
          <Select
            value={settings.language}
            onChange={(value) => onChange('language', value)}
            options={languages}
            fullWidth
          />
        </CardBody>
      </Card>

      <Card>
        <CardHeader title={t('settings.autoRefresh')} />
        <CardBody>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">{t('settings.autoRefresh')}</span>
              <Toggle
                checked={settings.autoRefresh}
                onChange={(checked) => onChange('autoRefresh', checked)}
              />
            </div>

            {settings.autoRefresh && (
              <Input
                type="number"
                label={t('settings.refreshInterval')}
                value={settings.refreshInterval}
                onChange={(e) => onChange('refreshInterval', parseInt(e.target.value))}
                min={1000}
                max={60000}
                fullWidth
              />
            )}
          </div>
        </CardBody>
      </Card>
    </div>
  );
};

// 数据设置组件
const DataSettings: React.FC<{
  settings: SystemSettings;
  onChange: (key: keyof SystemSettings, value: any) => void;
}> = ({ settings, onChange }) => {
  const { t } = useTranslation();
  return (
    <Card>
      <CardHeader title={t('settings.dataSettings')} />
      <CardBody>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-700">{t('settings.autoSave')}</div>
              <div className="text-xs text-gray-500 mt-1">
                {t('settings.autoSaveDesc')}
              </div>
            </div>
            <Toggle
              checked={settings.autoSave}
              onChange={(checked) => onChange('autoSave', checked)}
            />
          </div>

          <Input
            type="number"
            label={t('settings.maxHistory')}
            value={settings.maxHistory}
            onChange={(e) => onChange('maxHistory', parseInt(e.target.value))}
            min={10}
            max={1000}
            fullWidth
          />
        </div>
      </CardBody>
    </Card>
  );
};

export default SystemSettings;
