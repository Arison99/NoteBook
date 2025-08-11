import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PDFList from '../components/PDFList';
import PDFPreview from '../components/PDFPreview';

export default function PDFsPage() {
  const [selectedPDF, setSelectedPDF] = useState(null);
  const [pdfData, setPdfData] = useState(null);

  // Fetch PDF data when a PDF is selected
  useEffect(() => {
    if (selectedPDF && selectedPDF.id) {
      console.log('PDFsPage: Fetching PDF data for ID:', selectedPDF.id);
      fetch('http://localhost:5000/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: `query { pdfData(id: \"${selectedPDF.id}\") }` })
      })
        .then(res => {
          console.log('PDFsPage: GraphQL response status:', res.status);
          return res.json();
        })
        .then(res => {
          console.log('PDFsPage: GraphQL response:', res);
          if (res.errors) {
            console.error('PDFsPage: GraphQL errors:', res.errors);
          }
          setPdfData(res.data?.pdfData || null);
        })
        .catch(err => {
          console.error('PDFsPage: Error fetching PDF data:', err);
          setPdfData(null);
        });
    } else {
      setPdfData(null);
    }
  }, [selectedPDF]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">PDF Library</h1>
          <p className="text-gray-600 mt-1">Browse and view your encrypted PDF documents</p>
        </div>
        <Link
          to="/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Upload PDF</span>
        </Link>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* PDF List */}
        <div>
          <PDFList onSelect={setSelectedPDF} />
        </div>

        {/* PDF Preview */}
        <div>
          {selectedPDF ? (
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">PDF Preview</h2>
                  <p className="text-gray-600 text-sm">{selectedPDF.filename}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                    {selectedPDF.category}
                  </span>
                  {selectedPDF.compressed && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                      Encrypted & Compressed
                    </span>
                  )}
                </div>
              </div>
              <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-auto">
                <PDFPreview 
                  fileData={pdfData} 
                  filename={selectedPDF.filename} 
                  pdfId={selectedPDF.id}
                />
              </div>
              <div className="mt-4 flex justify-between items-center text-sm text-gray-500">
                <span>File ID: {selectedPDF.id}</span>
                <button
                  onClick={() => setSelectedPDF(null)}
                  className="text-red-600 hover:text-red-700 font-medium"
                >
                  Close Preview
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <div className="text-center py-12">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No PDF Selected</h3>
                <p className="text-gray-500">Select a PDF from the list to view its contents</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
