import React from 'react';
import Analytics from '../components/Analytics/Analytics';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-1">Detailed insights into your PDF library usage and storage</p>
      </div>

      {/* Analytics Component */}
      <Analytics />

      {/* Additional Analytics Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Trends */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Usage Trends</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Daily Uploads</span>
              <span className="font-semibold text-gray-800">5.2 avg</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Weekly Views</span>
              <span className="font-semibold text-gray-800">156</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Most Active Day</span>
              <span className="font-semibold text-gray-800">Tuesday</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Peak Usage Time</span>
              <span className="font-semibold text-gray-800">2-4 PM</span>
            </div>
          </div>
        </div>

        {/* Security Stats */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Security Statistics</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Encrypted Files</span>
              <span className="font-semibold text-green-600">100%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Compression Ratio</span>
              <span className="font-semibold text-gray-800">73%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Storage Saved</span>
              <span className="font-semibold text-green-600">2.1 GB</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Backup</span>
              <span className="font-semibold text-gray-800">2 hours ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">98.5%</div>
            <div className="text-gray-600 text-sm">Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">1.2s</div>
            <div className="text-gray-600 text-sm">Avg Load Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">99.9%</div>
            <div className="text-gray-600 text-sm">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600 mb-1">24ms</div>
            <div className="text-gray-600 text-sm">Response Time</div>
          </div>
        </div>
      </div>

      {/* Data Insights */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-lg text-white p-6">
        <h2 className="text-xl font-semibold mb-4">Key Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="font-semibold mb-2">📈 Growing Library</h3>
            <p className="text-purple-100 text-sm">Your PDF collection has grown 34% this month with consistent daily uploads.</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="font-semibold mb-2">🔒 Perfect Security</h3>
            <p className="text-purple-100 text-sm">All files remain encrypted with zero security incidents detected.</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="font-semibold mb-2">⚡ Optimal Performance</h3>
            <p className="text-purple-100 text-sm">System performance is excellent with fast upload and retrieval times.</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="font-semibold mb-2">💾 Storage Efficient</h3>
            <p className="text-purple-100 text-sm">Compression algorithms saving significant storage space automatically.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
