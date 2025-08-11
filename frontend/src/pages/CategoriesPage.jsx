import React, { useState } from 'react';
import CategoryList from '../components/CategoryList';
import CategoryCreate from '../components/CategoryCreate';

export default function CategoriesPage() {
  const [refresh, setRefresh] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const handleCategoryCreated = () => {
    setRefresh(r => !r);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Category Management</h1>
        <p className="text-gray-600 mt-1">Organize your PDFs with custom categories</p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Categories List */}
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Existing Categories</h2>
            <CategoryList 
              onSelect={setSelectedCategory}
              refresh={refresh}
            />
          </div>
        </div>

        {/* Create Category & Details */}
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Create New Category</h2>
            <CategoryCreate onCreated={handleCategoryCreated} />
          </div>

          {/* Category Details */}
          {selectedCategory && (
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Category Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-600">Name</label>
                  <p className="text-gray-800">{selectedCategory.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">ID</label>
                  <p className="text-gray-500 text-sm font-mono">{selectedCategory.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">PDF Count</label>
                  <p className="text-gray-800">{selectedCategory.pdf_ids?.length || 0} documents</p>
                </div>
                {selectedCategory.pdf_ids && selectedCategory.pdf_ids.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Associated PDFs</label>
                    <div className="mt-1 space-y-1">
                      {selectedCategory.pdf_ids.map(pdfId => (
                        <div key={pdfId} className="text-sm text-gray-500 font-mono bg-gray-50 px-2 py-1 rounded">
                          {pdfId}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="mt-4 flex space-x-2">
                <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors">
                  Edit
                </button>
                <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors">
                  Delete
                </button>
                <button 
                  onClick={() => setSelectedCategory(null)}
                  className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Category Management Tips */}
      <div className="bg-blue-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-3">Category Management Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-blue-700">
          <div className="flex items-start space-x-2">
            <svg className="w-5 h-5 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium">Use Descriptive Names</p>
              <p className="text-sm text-blue-600">Choose clear, specific category names for easy organization</p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <svg className="w-5 h-5 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <div>
              <p className="font-medium">Keep It Organized</p>
              <p className="text-sm text-blue-600">Create categories that match your workflow and needs</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
