import React, { useState, useEffect } from 'react';

// Placeholder version - API disabled
export default function CostDashboard() {
  const [costData, setCostData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [costByArea, setCostByArea] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const password = 'mission2024';

  // Load cost data (no API calls needed - just read logs)
  const loadCosts = async () => {
    try {
      const response = await fetch('/api/costs', {
        headers: { 'X-Password': password }
      });
      const data = await response.json();
      setCostData(data);
    } catch (error) {
      console.error('Error loading costs:', error);
    }
  };

  // Load anomaly data
  const loadAnomalies = async () => {
    try {
      const response = await fetch('/api/cost-anomalies', {
        headers: { 'X-Password': password }
      });
      const data = await response.json();
      setAnomalies(data.anomalies || []);
      setCostByArea(data.cost_by_area || []);
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error('Error loading anomalies:', error);
    }
  };

  useEffect(() => {
    loadCosts();
    loadAnomalies();
    const interval = setInterval(() => {
      loadCosts();
      loadAnomalies();
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Return placeholder while API is disabled
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
          <p className="text-2xl font-bold text-orange-600">⚠️ OVER</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h4 className="font-semibold mb-2">Next Steps</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>✓ Email/Calendar features disabled to stop token leak</li>
          <li>✓ Core router (Phi/Claude) still functional</li>
          <li>⏳ Awaiting cost stabilization (30+ min)</li>
          <li>⏳ Will rebuild email/calendar with proper isolation</li>
        </ul>
      </div>
    </div>
  );
  
  /* Original code disabled - keeping for reference
  if (!costData) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <p className="text-gray-600">Loading cost data...</p>
      </div>
    );
  }

  const today = costData.today || {};
  const stats = costData.daily_stats || {};
  const limits = costData.limits || {};
  
  // Default values if no data
  if (!today.total) {
    today.total = 0;
    today.email = 0;
    today.calendar = 0;
    today.other = 0;
    today.email_count = 0;
    today.calendar_count = 0;
    today.other_count = 0;
  }

  // Calculate percentages
  const dailyUsed = (today.total || 0) / (limits.daily_budget || 0.50);
  const emailUsed = (stats.email_today || 0) / (limits.daily_budget || 0.50);

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6">Cost Dashboard</h2>

      {/* Daily Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded">
          <p className="text-sm text-gray-600">Today's Cost</p>
          <p className="text-2xl font-bold">${(today.total || 0).toFixed(4)}</p>
          <p className="text-xs text-gray-500">Limit: ${limits.daily_budget || 0.50}</p>
        </div>

        <div className="bg-green-50 p-4 rounded">
          <p className="text-sm text-gray-600">Emails Processed</p>
          <p className="text-2xl font-bold">{today.emails || 0}</p>
          <p className="text-xs text-gray-500">Limit: {limits.max_emails || 50}</p>
        </div>

        <div className="bg-purple-50 p-4 rounded">
          <p className="text-sm text-gray-600">Claude Calls</p>
          <p className="text-2xl font-bold">{today.claude_calls || 0}</p>
          <p className="text-xs text-gray-500">Limit: {limits.max_claude || 10}</p>
        </div>

        <div className="bg-orange-50 p-4 rounded">
          <p className="text-sm text-gray-600">Monthly Estimate</p>
          <p className="text-2xl font-bold">${(today.total * 30).toFixed(2)}</p>
          <p className="text-xs text-gray-500">If daily avg continues</p>
        </div>
      </div>

      {/* Progress Bars */}
      <div className="mb-6 space-y-4">
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium">Daily Budget</span>
            <span className="text-sm">${(today.total || 0).toFixed(4)} / ${limits.daily_budget || 0.50}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${dailyUsed > 0.8 ? 'bg-red-500' : dailyUsed > 0.5 ? 'bg-yellow-500' : 'bg-green-500'}`}
              style={{ width: `${Math.min(dailyUsed * 100, 100)}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium">Email Processing</span>
            <span className="text-sm">{today.emails || 0} / {limits.max_emails || 50}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500"
              style={{ width: `${Math.min(((today.emails || 0) / (limits.max_emails || 50)) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Cost Breakdown Today */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">Cost Breakdown (Today)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <p className="text-sm text-gray-600">Email</p>
            <p className="text-xl font-bold">${(today.email || 0).toFixed(4)}</p>
            <p className="text-xs text-gray-500">{today.email_count || 0} transactions</p>
          </div>

          <div className="bg-gray-50 p-4 rounded">
            <p className="text-sm text-gray-600">Calendar</p>
            <p className="text-xl font-bold">${(today.calendar || 0).toFixed(4)}</p>
            <p className="text-xs text-gray-500">{today.calendar_count || 0} transactions</p>
          </div>

          <div className="bg-gray-50 p-4 rounded">
            <p className="text-sm text-gray-600">Tasks & Classification</p>
            <p className="text-xl font-bold">${(today.other || 0).toFixed(4)}</p>
            <p className="text-xs text-gray-500">{today.other_count || 0} transactions</p>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {(today.recent_transactions || []).map((txn, idx) => (
            <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
              <span className="font-medium">{txn.type}</span>
              <span className="text-gray-600">{txn.details}</span>
              <span className="font-bold">${txn.cost.toFixed(4)}</span>
            </div>
          ))}
          {(!today.recent_transactions || today.recent_transactions.length === 0) && (
            <p className="text-gray-500 text-sm">No transactions yet today</p>
          )}
        </div>
      </div>

      {/* Weekly Trend */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Weekly Trend</h3>
        <div className="space-y-2">
          {Object.entries(stats)
            .slice(-7)
            .map(([date, data]) => (
              <div key={date} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span className="text-sm">{new Date(date).toLocaleDateString()}</span>
                <div className="flex-1 mx-4 bg-gray-200 rounded h-6" style={{ maxWidth: '200px' }}>
                  <div
                    className="bg-blue-500 h-6 rounded"
                    style={{ width: `${Math.min((data.total / 0.50) * 100, 100)}%` }}
                  />
                </div>
                <span className="font-bold text-sm">${data.total.toFixed(4)}</span>
              </div>
            ))}
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded">
          <h4 className="font-semibold mb-3 text-red-900">Cost Alerts</h4>
          <div className="space-y-2">
            {alerts.map((alert, idx) => (
              <div key={idx} className={`p-2 rounded text-sm ${alert.level === 'ERROR' ? 'bg-red-100 text-red-900' : 'bg-yellow-100 text-yellow-900'}`}>
                <strong>[{alert.level}]</strong> {alert.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cost Leaks (Anomalies) */}
      {anomalies.length > 0 && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h4 className="font-semibold mb-3">⚠️ Potential Cost Leaks Detected</h4>
          <div className="space-y-3">
            {anomalies.map((anomaly, idx) => (
              <div key={idx} className="p-3 bg-white rounded border border-yellow-300">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{anomaly.type}</p>
                    <p className="text-sm text-gray-600">
                      {anomaly.deviation_pct 
                        ? `${anomaly.deviation_pct.toFixed(0)}% above baseline`
                        : anomaly.deviation
                      }
                    </p>
                    <p className="text-xs text-gray-500">
                      {anomaly.count} operations today
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg">${anomaly.today_cost.toFixed(4)}</p>
                    {anomaly.baseline_avg && (
                      <p className="text-xs text-gray-600">
                        Baseline: ${anomaly.baseline_avg.toFixed(4)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cost by Area (Where tokens are going) */}
      {costByArea.length > 0 && (
        <div className="mt-6 p-4 bg-indigo-50 border border-indigo-200 rounded">
          <h4 className="font-semibold mb-3">💸 Where Tokens Are Going (Top 10)</h4>
          <div className="space-y-2">
            {costByArea.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center p-2 bg-white rounded text-sm">
                <span className="max-w-xs truncate">{item.area}</span>
                <div className="flex items-center gap-4">
                  <span className="text-gray-600">{item.count} ops</span>
                  <span className="font-bold min-w-16 text-right">${item.cost.toFixed(4)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rate Limits Info */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h4 className="font-semibold mb-2">Rate Limits</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>✓ Max {limits.max_emails || 50} emails/day (prevents runaway email processing)</li>
          <li>✓ Max {limits.max_claude || 10} Claude calls/day (controls AI inference costs)</li>
          <li>✓ Max ${limits.daily_budget || 0.50}/day budget (hard stop on spending)</li>
          <li>✓ Auto-filtering blocks {limits.auto_filter_blocks || 80}% of spam/notifications</li>
        </ul>
      </div>
    </div>
  );
}
