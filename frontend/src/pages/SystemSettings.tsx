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
import { addNotification } from '../store/slices/uiSlice';
import { Card, CardBody, CardHeader } from '../components/ui/cards/Card';
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

  const saveSettings = async () => {
    setIsSaving(true);
    try {
      localStorage.setItem('systemSettings', JSON.stringify(settings));
      setHasUnsavedChanges(false);
      dispatch(addNotification({
        type: 'success',
        title: '保存成功',
        message: '系统设置已保存',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '保存失败',
        message: '无法保存设置',
      }));
    } finally {
      setIsSaving(false);
    }
  };

  const resetSettings = = () => {
    if (!confirm('确定要重置所有设置为默认值吗？')) return;

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
      language: 'zh-CN',
      autoRefresh: true,
      refreshInterval: 2000,
      autoSave: true,
      maxHistory: 100,
    };

    setSettings(defaultSettings);
    setHasUnsavedChanges(true);
  };

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    setSettings({ ...settings, [key]: value });
    setHasUnsavedChanges(true);
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${settings.apiBaseUrl}/health`);
      if (response.ok) {
        dispatch(addNotification({
          type: 'success',
          title: '连接成功',
          message: 'API服务器连接正常',
        }));
      } else {
        throw new Error('Server returned error');
      }
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '连接失败',
        message: '无法连接到API服务器',
      }));
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">系统设置</h1>
          <p className="text-sm text-gray-600 mt-1">
            配置系统参数和偏好设置
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            onClick={resetSettings}
          >
            重置默认
          </Button>
          <Button
            variant="primary"
            onClick={saveSettings}
            loading={isSaving}
            leftIcon={<SaveIcon size={16} />}
            disabled={!hasUnsavedChanges}
          >
            保存设置
          </Button>
        </div>
      </div>

      {/* 未保存提示 */}
      {hasUnsavedChanges && (
        <Alert variant="warning" title="有未保存的更改">
          请保存设置以使更改生效
        </Alert>
      )}

      {/* 标签页导航 */}
      <div className="flex gap-2 border-b border-gray-200">
        <TabButton
          active={activeTab === 'api'}
          label="API配置"
          onClick={() => setActiveTab('api')}
        />
        <TabButton
          active={activeTab === 'simulation'}
          label="仿真参数"
          onClick={() => setActiveTab('simulation')}
        />
        <TabButton
          active={activeTab === 'display'}
          label="显示设置"
          onClick={() => setActiveTab('display')}
        />
        <TabButton
          active={activeTab === 'data'}
          label="数据设置"
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
}> = {
  active, label, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium transition-colors border-bkt-2 ${
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
  return (
    <Card>
      <CardHeader
        title="API配置"
        subtitle="配置后端API连接参数"
      />
      <CardBody>
        <div className="space-y-4">
          <Input
            label="API基础URL"
            value={settings.apiBaseUrl}
            onChange={(e) => onChange('apiBaseUrl', e.target.value)}
            placeholder="http://localhost:8000"
            fullWidth
          />

          <Input
            type="number"
            label="API超时时间（毫秒）"
            value={settings.apiTimeout}
            onChange={(e) => onChange('apiTimeout', parseInt(e.target.value))}
            min={1000}
            max={300000}
            fullWidth
          />

          <Input
            label="WebSocket URL"
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
              测试连接
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
  return (
    <Card>
      <CardHeader
        title="仿真参数默认值"
        subtitle="设置新建仿真时的默认参数"
      />
      <CardBody>
        <div className="space-y-4">
          <Input
            type="number"
            label="默认总轮数"
            value={settings.defaultTotalRounds}
            onChange={(e) => onChange('defaultTotalRounds', parseInt(e.target.value))}
            min={1}
            max={1000}
            fullWidth
          />

          <Input
            type="number"
            label="默认轮次时长（月）"
            value={settings.defaultRoundDuration}
            onChange={(e) => onChange('defaultRoundDuration', parseInt(e.target.value))}
            min={1}
            max={12}
            fullWidth
          />

          <Input
            type="number"
            label="默认随机事件概率"
            value={settings.defaultRandomEventProb}
            onChange={(e) => onChange('defaultRandomEventProb', parseFloat(e.target.value))}
            min={0}
            max={1}
            step={0.01}
            fullWidth
          />

          <Input
            type="number"
            label="默认检查点间隔"
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
const DisplaySettings: React.FC<{
  settings: SystemSettings;
  onChange: (key: keyof SystemSettings, value: any) => void;
}> = ({ settings, onChange }) => {
  const themes = [
    { value: 'light', label: '浅色' },
    { value: 'dark', label: '深色' },
    { value: 'auto', label: '自动' },
  ];

  const languages = [
    { value: 'zh-CN', label: '简体中文' },
    { value: 'en-US', label: 'English' },
  ];

  const accentColors = [
    { value: '#3B82F6', label: '蓝色', color: '#3B82F6' },
    { value: '#10B981', label: '绿色', color: '#10B981' },
    { value: '#F59E0B', label: '橙色', color: '#F59E0B' },
    { value: '#EF4444', label: '红色', color: '#EF4444' },
    { value: '#8B5CF6', label: '紫色', color: '#8B5CF6' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader title="主题设置" />
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                主题模式
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
                强调色
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
        <CardHeader title="语言设置" />
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
        <CardHeader title="自动刷新设置" />
        <CardBody>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">启用自动刷新</span>
              <Toggle
                checked={settings.autoRefresh}
                onChange={(checked) => onChange('autoRefresh', checked)}
              />
            </div>

            {settings.autoRefresh && (
              <Input
                type="number"
                label="刷新间隔（毫秒）"
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
  return (
    <Card>
      <CardHeader title="数据管理设置" />
      <CardBody>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-700">自动保存</div>
              <div className="text-xs text-gray-500 mt-1">
                自动保存仿真进度和结果
              </div>
            </div>
            <Toggle
              checked={settings.autoSave}
              onChange={(checked) => onChange('autoSave', checked)}
            />
          </div>

          <Input
            type="number"
            label="最大历史记录数"
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

export default SystemSettings;
