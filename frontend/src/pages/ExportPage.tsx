/**
 * 结果导出页面
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { addNotification } from '../store/slices/uiSlice';
import api from '../services/api';

// 导出配置组件
const ExportConfig: React.FC = ({ onExport }: { onExport: (config: ExportOptions) => void }) => {
  const [config, setConfig] = useState<ExportOptions>({
    format: 'json',
    includeAgents: true,
    includeInteractions: true,
    includeMetrics: true,
    includeEvents: true,
    includeReasoning: false,
    dateRange: {
      start: '',
      end: '',
    },
    roundRange: {
      start: 0,
      end: 0,
    },
  });

  const handleFormatChange = (format: ExportFormat) => {
    setConfig({ ...config, format });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onExport(config);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">导出配置</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 导出格式选择 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            导出格式
          </label>
          <div className="grid grid-cols-4 gap-4">
            {(['json', 'csv', 'excel', 'pdf'] as ExportFormat[]).map((format) => (
              <button
                key={format}
                type="button"
                onClick={() => handleFormatChange(format)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  config.format === format
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-2">
                  {format === 'json' && '📄'}
                  {format === 'csv' && '📊'}
                  {format === 'excel' && '📈'}
                  {format === 'pdf' && '📑'}
                </div>
                <div className="font-medium">{format.toUpperCase()}</div>
              </button>
            ))}
          </div>
        </div>

        {/* 导出内容选择 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            导出内容
          </label>
          <div className="space-y-2">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.includeAgents}
                onChange={(e) => setConfig({ ...config, includeAgents: e.target.checked })}
                className="form-checkbox"
              />
              <span>智能体数据</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.includeInteractions}
                onChange={(e) => setConfig({ ...config, includeInteractions: e.target.checked })}
                className="form-checkbox"
              />
              <span>互动记录</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.includeMetrics}
                onChange={(e) => setConfig({ ...config, includeMetrics: e.target.checked })}
                className="form-checkbox"
              />
              <span>指标数据</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.includeEvents}
                onChange={(e) => setConfig({ ...config, includeEvents: e.target.checked })}
                className="form-checkbox"
              />
              <span>事件记录</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.includeReasoning}
                onChange={(e) => setConfig({ ...config, includeReasoning: e.target.checked })}
                className="form-checkbox"
              />
              <span>包含决策理由</span>
            </label>
          </div>
        </div>

        {/* 时间范围 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            时间范围
          </label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">开始时间</label>
              <input
                type="datetime-local"
                value={config.dateRange.start}
                onChange={(e) => setConfig({
                  ...config,
                  dateRange: { ...config.dateRange, start: e.target.value },
                })}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">结束时间</label>
              <input
                type="datetime-local"
                value={config.dateRange.end}
                onChange={(e) => setConfig({
                  ...config,
                  dateRange: { ...config.dateRange, end: e.target.value },
                })}
                className="w-full px-4 py-2 border rounded-lg"
              />
            </div>
          </div>
        </div>

        {/* 轮次范围 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            轮次范围
          </label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">起始轮次</label>
              <input
                type="number"
                value={config.roundRange.start}
                onChange={(e) => setConfig({
                  ...config,
                  roundRange: { ...config.roundRange, start: parseInt(e.target.value) || 0 },
                })}
                className="w-full px-4 py-2 border rounded-lg"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">结束轮次</label>
              <input
                type="number"
                value={config.roundRange.end}
                onChange={(e) => setConfig({
                  ...config,
                  roundRange: { ...config.roundRange, end: parseInt(e.target.value) || 0 },
                })}
                className="w-full px-4 py-2 border rounded-lg"
                min="0"
              />
            </div>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            开始导出
          </button>
        </div>
      </form>
    </div>
  );
};

// 导出预览组件
const ExportPreview: React.FC<{ data: any; config: ExportOptions }> = ({ data, config }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const itemsPerPage = 20;

  // 获取数据数组
  const dataArray = Array.isArray(data) ? data : [];
  const totalItems = dataArray.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  // 排序
  const sortedData = [...dataArray].sort((a, b) => {
    if (!sortField) return 0;
    const aValue = a[sortField];
    const bValue = b[sortField];

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    }

    const aString = String(aValue || '');
    const bString = String(bValue || '');

    return sortOrder === 'asc'
      ? aString.localeCompare(bString)
      : bString.localeCompare(aString);
  });

  // 分页
  const paginatedData = sortedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const getColumns = () => {
    if (paginatedData.length === 0) return [];
    return Object.keys(paginatedData[0]);
  };

  const formatCellValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'boolean') return value ? '是' : '否';
    return String(value);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">数据预览</h2>
        <div className="text-sm text-gray-600">
          共 {totalItems} 条记录
        </div>
      </div>

      {/* 表格 */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left">序号</th>
              {getColumns().map((column) => (
                <th
                  key={column}
                  className="px-4 py-2 text-left cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort(column)}
                >
                  <div className="flex items-center">
                    {column}
                    {sortField === column && (
                      <span className="ml-1">
                        {sortOrder === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {paginatedData.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-600">
                  {(currentPage - 1) * itemsPerPage + index + 1}
                </td>
                {getColumns().map((column) => (
                  <td key={column} className="px-4 py-2">
                    {formatCellValue(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分页控件 */}
      <div className="flex justify-between items-center mt-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <span className="text-sm">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm">跳转到</span>
          <input
            type="number"
            value={currentPage}
            onChange={(e) => {
              const page = parseInt(e.target.value);
              if (page >= 1 && page <= totalPages) {
                setCurrentPage(page);
              }
            }}
            className="w-16 px-2 py-1 border rounded"
            min="1"
            max={totalPages}
          />
        </div>
      </div>
    </div>
  );
};

// 导出选项类型
type ExportFormat = 'json' | 'csv' | 'excel' | 'pdf';

interface ExportOptions {
  format: ExportFormat;
  includeAgents: boolean;
  includeInteractions: boolean;
  includeMetrics: boolean;
  includeEvents: boolean;
  includeReasoning: boolean;
  dateRange: {
    start: string;
    end: string;
  };
  roundRange: {
    start: number;
    end: number;
  };
}

// 主页面组件
const ExportPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentSimulation } = useSelector((state: RootState) => state.simulation);
  const [isExporting, setIsExporting] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [currentConfig, setCurrentConfig] = useState<ExportOptions | null>(null);

  const handleExport = async (config: ExportOptions) => {
    if (!currentSimulation) {
      dispatch(addNotification({
        type: 'error',
        title: '导出失败',
        message: '请先选择一个仿真',
      }));
      return;
    }

    setIsExporting(true);
    setCurrentConfig(config);

    try {
      // 请求预览数据
      const response = await api.post('/export/preview', {
        simulation_id: currentSimulation.id,
        ...config,
      });
      setPreviewData(response.data);

      // 执行实际导出
      const exportResponse = await api.post('/export', {
        simulation_id: currentSimulation.id,
        ...config,
      }, {
        responseType: 'blob',
      });

      // 下载文件
      const url = window.URL.createObjectURL(new Blob([exportResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `simulation_${currentSimulation.id}.${config.format}`;
      link.click();
      window.URL.revokeObjectURL(url);

      dispatch(addNotification({
        type: 'success',
        title: '导出成功',
        message: '文件已下载',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '导出失败',
        message: '无法导出数据',
      }));
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">结果导出</h1>

      {/* 仿真信息 */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
        {currentSimulation ? (
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm text-blue-600">当前仿真</div>
              <div className="text-lg font-semibold">{currentSimulation.name}</div>
            </div>
            <div className="text-sm text-blue-600">
              轮次: {currentSimulation.current_round} / {currentSimulation.total_rounds}
            </div>
          </div>
        ) : (
          <div className="text-blue-700">
            请先在仿真管理页面选择一个仿真
          </div>
        )}
      </div>

      {/* 导出配置 */}
      <ExportConfig onExport={handleExport} />

      {/* 预览区域 */}
      {isExporting && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">正在导出数据...</p>
        </div>
      )}

      {previewData && currentConfig && (
        <ExportPreview data={previewData} config={currentConfig} />
      )}

      {/* 导出说明 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">导出说明</h3>
        <div className="space-y-3">
          <div>
            <h4 className="font-medium mb-2">支持的格式</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              <li><strong>JSON</strong> - 适合程序处理和进一步分析</li>
              <li><strong>CSV</strong> - 适合Excel和数据分析工具</li>
              <li><strong>Excel</strong> - 包含多个工作表的完整报告</li>
              <li><strong>PDF</strong> - 适合打印和分享的可视化报告</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">注意事项</h4>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              <li>包含决策理由会显著增加文件大小</li>
              <li>导出大量数据可能需要较长时间</li>
              <li>PDF报告会自动生成图表和可视化</li>
              <li>Excel文件包含数据和分析两个工作表</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportPage;
