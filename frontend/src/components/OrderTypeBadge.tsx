import React from 'react';

interface OrderTypeBadgeProps {
  orderType: string;
  showChinese?: boolean;
}

const OrderTypeBadge: React.FC<OrderTypeBadgeProps> = ({ orderType, showChinese = true }) => {
  const getOrderTypeInfo = () => {
    switch (orderType) {
      case 'multipolar':
        return {
          label: 'Multipolar',
          labelZh: '多极化',
          color: 'bg-blue-100 text-blue-700 border-blue-300',
          icon: '🌐',
        };
      case 'bipolar':
        return {
          label: 'Bipolar',
          labelZh: '两极化',
          color: 'bg-purple-100 text-purple-700 border-purple-300',
          icon: '⚖️',
        };
      case 'unipolar_hegemonic':
        return {
          label: 'Unipolar Hegemonic',
          labelZh: '单极霸权',
          color: 'bg-red-100 text-red-700 border-red-300',
          icon: '👑',
        };
      case 'hierarchical':
        return {
          label: 'Hierarchical',
          labelZh: '等级秩序',
          color: 'bg-amber-100 text-amber-700 border-amber-300',
          icon: '🏛️',
        };
      default:
        return {
          label: 'Unknown',
          labelZh: '未知',
          color: 'bg-gray-100 text-gray-700 border-gray-300',
          icon: '❓',
        };
    }
  };

  const info = getOrderTypeInfo();

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${info.color}`}>
      <span>{info.icon}</span>
      <span>{info.label}</span>
      {showChinese && <span className="text-xs opacity-75">({info.labelZh})</span>}
    </span>
  );
};

export default OrderTypeBadge;
