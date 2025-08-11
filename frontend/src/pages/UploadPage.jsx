import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PDFUpload from '../components/PDFUpload';

export default function UploadPage() {
  const [categories, setCategories] = useState([]);
  const [refresh, setRefresh] = useState(false);
  const navigate = useNavigate();

  // Fetch categories for PDFUpload
  useEffect(() => {
    fetch('http://localhost:5000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '{ categories { id name } }' })
    })
      .then(res => res.json())
      .then(res => setCategories(res.data.categories || []))
      .catch(err => console.error('Error fetching categories:', err));
  }, [refresh]);

  const handleUploadSuccess = () => {
    // Redirect to PDFs page after successful upload
    navigate('/pdfs');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800">Upload PDF</h1>
        <p className="text-gray-600 mt-2">Upload a new PDF document to your encrypted library</p>
      </div>

      {/* Upload Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <PDFUpload 
            categories={categories} 
            onUploaded={handleUploadSuccess} 
          />
        </div>

        {/* Upload Instructions */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Instructions</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">1</span>
              </div>
              <div>
                <p className="font-medium text-gray-800">Select Your PDF</p>
                <p className="text-gray-600 text-sm">Choose a PDF file from your computer (drag & drop supported)</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">2</span>
              </div>
              <div>
                <p className="font-medium text-gray-800">Choose Category</p>
                <p className="text-gray-600 text-sm">Select an existing category or create a new one</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                <span className="text-blue-600 font-semibold text-sm">3</span>
              </div>
              <div>
                <p className="font-medium text-gray-800">Automatic Processing</p>
                <p className="text-gray-600 text-sm">Your PDF will be encrypted and compressed automatically</p>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-green-800 font-medium">Security Features</p>
            </div>
            <ul className="mt-2 text-green-700 text-sm space-y-1">
              <li>• End-to-end encryption</li>
              <li>• Automatic compression</li>
              <li>• Secure storage</li>
              <li>• Distributed backup</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Category Management Link */}
      <div className="text-center">
        <p className="text-gray-600">
          Need to create a new category?{' '}
          <button
            onClick={() => navigate('/categories')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Manage Categories
          </button>
        </p>
      </div>
    </div>
  );
}
