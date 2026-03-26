import React from 'react';

// Simple placeholder while API is disabled
export default function CostDashboard() {
  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Cost Dashboard</h2>
      
      <div className="bg-yellow-50 p-4 rounded border border-yellow-200 mb-6">
        <p className="text-yellow-900 font-semibold">⚠️ Feature Disabled</p>
        <p className="text-sm text-yellow-800">Cost dashboard API is temporarily disabled to investigate token usage.</p>
        <p className="text-sm text-yellow-800 mt-2">Total spent today: <strong>$10.62</strong></p>
      </div>
      
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm text-gray-600">Daily Budget</p>
          <p className="text-2xl font-bold">$0.50</p>
        </div>
        <div className="bg-red-50 p-4 rounded">
          <p className="text-sm text-gray-600">Amount Used</p>
          <p className="text-2xl font-bold text-red-600">$10.62</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <p className="text-sm text-gray-600">Remaining</p>
          <p className="text-2xl font-bold text-red-600">-$10.12</p>
        </div>
        <div className="bg-orange-50 p-4 rounded">
          <p className="text-sm text-gray-600">Status</p>
          <p className="text-2xl font-bold text-orange-600">OVER BUDGET</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h4 className="font-semibold mb-2">Status</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>✓ Email/Calendar features disabled</li>
          <li>✓ Core router (Phi/Claude) functional</li>
          <li>⏳ Awaiting cost stabilization</li>
          <li>⏳ Will rebuild with proper isolation</li>
        </ul>
      </div>
    </div>
  );
}
