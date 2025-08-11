import React from 'react';

export default function Dashboard({ children }) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Manage your encrypted PDF documents and categories</p>
      </div>
      {children}
    </div>
  );
}
