import React from 'react';

const StatCard = ({ title, value, icon: Icon, trend }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500 mb-1">{title}</p>
        <h4 className="text-2xl font-bold text-gray-900">{value}</h4>
        {trend && <span className="text-xs text-green-500 font-medium">{trend}</span>}
      </div>
      <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
        <Icon size={24} />
      </div>
    </div>
  );
};

export default StatCard;