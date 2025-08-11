import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">NoteBook</h3>
            </div>
            <p className="text-sm mb-4">
              A distributed PDF management system with encryption, compression, and GraphQL API. 
              Built with Flask, CouchDB, React, and modern web technologies.
            </p>
            <div className="flex space-x-4">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                React + Tailwind
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Flask + GraphQL
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                CouchDB
              </span>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Features</h4>
            <ul className="space-y-2 text-sm">
              <li>• PDF Encryption & Compression</li>
              <li>• Distributed Database Sync</li>
              <li>• Category Management</li>
              <li>• Real-time Analytics</li>
              <li>• GraphQL API</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Technology</h4>
            <ul className="space-y-2 text-sm">
              <li>• Domain-Driven Design</li>
              <li>• Apollo Client</li>
              <li>• Cryptography</li>
              <li>• PDF.js Integration</li>
              <li>• Responsive Design</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm">&copy; 2025 NoteBook. Student project for learning distributed systems.</p>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <span className="text-xs bg-slate-800 px-2 py-1 rounded">v1.0.0</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-xs">All systems operational</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
