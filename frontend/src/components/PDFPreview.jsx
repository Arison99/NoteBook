import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import TableOfContents from './TableOfContents';
import OfflineIndicator from './OfflineIndicator';
import FullscreenPDFViewer from './FullscreenPDFViewer';
import { OfflineStorage } from '../utils/offlineStorage';

// Configure PDF.js worker with CDN (works better with React builds)
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function PDFPreview({ fileData, filename = "document.pdf", pdfId, className = "" }) {
  const [numPages, setNumPages] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rotation, setRotation] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [pageWidth, setPageWidth] = useState(null);
  const [fitMode, setFitMode] = useState('auto');
  const [outline, setOutline] = useState(null);
  const [showToC, setShowToC] = useState(false);
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const [offlineData, setOfflineData] = useState(null);
  const [showAlternativeFullscreen, setShowAlternativeFullscreen] = useState(false);

  // Process PDF data - either from props or offline cache
  const pdfData = useMemo(() => {
    let dataToProcess = fileData || offlineData;
    
    if (!dataToProcess) {
      console.log('PDFPreview: No fileData provided');
      return null;
    }
    try {
      console.log('PDFPreview: Processing fileData, length:', dataToProcess.length);
      const binaryData = Uint8Array.from(atob(dataToProcess), c => c.charCodeAt(0));
      console.log('PDFPreview: Binary data length:', binaryData.length);
      return { data: binaryData };
    } catch (err) {
      console.error('PDFPreview: Error processing fileData:', err);
      setError('Invalid PDF data format');
      return null;
    }
  }, [fileData, offlineData]);

  // Check for offline data if no fileData provided
  useEffect(() => {
    if (!fileData && pdfId) {
      const loadOfflineData = async () => {
        try {
          setIsLoading(true);
          const cachedData = await OfflineStorage.getCachedPDF(pdfId);
          if (cachedData && cachedData.data) {
            setIsOfflineMode(true);
            setOfflineData(cachedData.data);
            console.log('PDFPreview: Loading from offline cache');
          } else {
            setError('PDF not available offline');
          }
        } catch (err) {
          console.error('Error loading offline PDF:', err);
          setError('Failed to load offline PDF');
        } finally {
          setIsLoading(false);
        }
      };
      loadOfflineData();
    }
  }, [fileData, pdfId]);

  // Extract Table of Contents when document loads
  const extractOutline = async (doc) => {
    try {
      // Check cache first
      if (pdfId) {
        const cachedOutline = await OfflineStorage.getCachedToC(pdfId);
        if (cachedOutline) {
          setOutline(cachedOutline);
          return;
        }
      }

      // Extract from document
      const rawOutline = await doc.getOutline();
      if (rawOutline && rawOutline.length > 0) {
        console.log('PDFPreview: Raw outline:', rawOutline);
        
        // Process outline to ensure proper format
        const processOutlineItem = async (item) => {
          const processedItem = {
            title: item.title || item.url || 'Untitled',
            dest: item.dest,
            items: []
          };

          // If dest is a string, resolve it to page number
          if (typeof item.dest === 'string') {
            try {
              const destObj = await doc.getDestination(item.dest);
              if (destObj && destObj[0]) {
                const pageRef = destObj[0];
                const pageIndex = await doc.getPageIndex(pageRef);
                processedItem.dest = { num: pageIndex + 1 };
              }
            } catch (e) {
              console.warn('Failed to resolve destination:', item.dest, e);
            }
          } else if (item.dest && Array.isArray(item.dest) && item.dest[0]) {
            // Direct destination array
            try {
              const pageRef = item.dest[0];
              const pageIndex = await doc.getPageIndex(pageRef);
              processedItem.dest = { num: pageIndex + 1 };
            } catch (e) {
              console.warn('Failed to resolve destination array:', item.dest, e);
            }
          }

          // Process child items recursively
          if (item.items && item.items.length > 0) {
            processedItem.items = await Promise.all(
              item.items.map(childItem => processOutlineItem(childItem))
            );
          }

          return processedItem;
        };

        const processedOutline = await Promise.all(
          rawOutline.map(item => processOutlineItem(item))
        );

        console.log('PDFPreview: Processed outline:', processedOutline);
        setOutline(processedOutline);
        
        // Cache the processed outline
        if (pdfId) {
          await OfflineStorage.cacheToC(pdfId, processedOutline);
        }
      } else {
        console.log('PDFPreview: No outline found in document');
        setOutline(null);
      }
    } catch (err) {
      console.error('PDFPreview: Error extracting outline:', err);
      setOutline(null);
    }
  };

  // Auto-fit when container size changes
  useEffect(() => {
    if (fitMode === 'auto' && pageWidth) {
      const container = document.getElementById('pdf-container');
      if (container) {
        const containerWidth = container.offsetWidth - 40;
        const newScale = containerWidth / pageWidth;
        setScale(Math.min(newScale, 1.5));
      }
    }
  }, [fitMode, pageWidth, isFullscreen]);

  const onDocumentLoadSuccess = useCallback((doc) => {
    console.log('PDFPreview: Document loaded successfully, pages:', doc.numPages);
    setNumPages(doc.numPages);
    setCurrentPage(1);
    setIsLoading(false);
    setError(null);
    extractOutline(doc);
  }, [pdfId]);

  const onDocumentLoadError = useCallback((error) => {
    console.error('PDFPreview: Document load error:', error);
    setError(`Failed to load PDF: ${error.message}`);
    setIsLoading(false);
  }, []);

  const onPageLoadSuccess = useCallback((page) => {
    if (!pageWidth) {
      setPageWidth(page.originalWidth);
    }
  }, [pageWidth]);

  // Navigation handlers
  const handlePreviousPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(numPages, prev + 1));
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(3.0, prev + 0.2));
    setFitMode('custom');
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(0.5, prev - 0.2));
    setFitMode('custom');
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleFitToWidth = () => {
    const container = document.getElementById('pdf-container');
    if (container && pageWidth) {
      const containerWidth = container.offsetWidth - 40;
      const newScale = containerWidth / pageWidth;
      setScale(newScale);
      setFitMode('width');
    }
  };

  const handleFitToPage = () => {
    setScale(1.0);
    setFitMode('page');
  };

  const handleFullscreen = () => {
    setIsFullscreen(prev => !prev);
  };

  const handleAlternativeFullscreen = () => {
    setShowAlternativeFullscreen(true);
  };

  const handleToggleToC = () => {
    setShowToC(prev => !prev);
  };

  const handleToCNavigation = (pageNum) => {
    if (pageNum >= 1 && pageNum <= numPages) {
      setCurrentPage(pageNum);
    }
  };

  const handleCacheChange = (isCached) => {
    console.log('Cache status changed:', isCached);
  };

  // Keyboard shortcuts
  const handleKeyDown = useCallback((e) => {
    if (!numPages) return;
    
    switch (e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        handlePreviousPage();
        break;
      case 'ArrowRight':
        e.preventDefault();
        handleNextPage();
        break;
      case '+':
      case '=':
        e.preventDefault();
        handleZoomIn();
        break;
      case '-':
        e.preventDefault();
        handleZoomOut();
        break;
      case 'r':
        e.preventDefault();
        handleRotate();
        break;
      case 'f':
        e.preventDefault();
        handleFullscreen();
        break;
      case 't':
        e.preventDefault();
        handleToggleToC();
        break;
      case 'Escape':
        if (isFullscreen) {
          e.preventDefault();
          setIsFullscreen(false);
        }
        break;
    }
  }, [numPages, isFullscreen]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Download and Print handlers
  const handleDownload = () => {
    if (!pdfData) return;
    
    try {
      const blob = new Blob([pdfData.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      setError('Failed to download PDF');
    }
  };

  const handlePrint = () => {
    if (!pdfData) return;
    
    try {
      const blob = new Blob([pdfData.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const printWindow = window.open(url);
      printWindow.onload = () => {
        printWindow.print();
        setTimeout(() => {
          printWindow.close();
          URL.revokeObjectURL(url);
        }, 100);
      };
    } catch (err) {
      console.error('Print failed:', err);
      setError('Failed to print PDF');
    }
  };

  // Render states
  if (!pdfData && !isLoading) {
    return (
      <div className={`flex flex-col items-center justify-center h-64 text-gray-500 ${className}`}>
        <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-lg font-medium">No PDF selected</p>
        <p className="text-sm">Select a document to preview</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center h-64 text-red-500 ${className}`}>
        <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-lg font-semibold">Error Loading PDF</p>
        <p className="text-sm text-center max-w-md">{error}</p>
        <div className="flex space-x-2 mt-4">
          <button 
            onClick={() => {
              setError(null);
              setIsLoading(true);
            }} 
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
          <button 
            onClick={() => setError(null)} 
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  const containerClass = isFullscreen 
    ? "fixed inset-0 z-50 bg-white flex" 
    : `flex ${showToC ? 'lg:flex-row' : 'flex-col'} h-full ${className}`;

  return (
    <div className={containerClass}>
      {/* Table of Contents Sidebar */}
      {showToC && outline && (
        <div className={`${isFullscreen ? 'w-80' : 'w-full lg:w-80'} border-r border-gray-200 bg-gray-50 flex-shrink-0 overflow-hidden`}>
          <TableOfContents 
            outline={outline} 
            onNavigate={handleToCNavigation}
            currentPage={currentPage}
            className="h-full overflow-y-auto"
          />
        </div>
      )}

      {/* Main PDF View */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between p-4 bg-gray-100 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700 truncate max-w-xs">
              {filename}
            </span>
            {numPages && (
              <span className="text-xs text-gray-500 whitespace-nowrap">
                ({numPages} page{numPages !== 1 ? 's' : ''})
              </span>
            )}
            {isOfflineMode && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                Offline
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            {/* Offline Indicator */}
            {pdfId && (
              <OfflineIndicator 
                pdfId={pdfId}
                pdfData={fileData}
                filename={filename}
                onCacheChange={handleCacheChange}
              />
            )}

            {/* Table of Contents Button */}
            {outline && outline.length > 0 && (
              <button
                onClick={handleToggleToC}
                className={`p-2 rounded transition-colors ${
                  showToC 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200'
                }`}
                title="Toggle Table of Contents (T)"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </button>
            )}

            {/* Fit Controls */}
            <div className="flex items-center space-x-1 mr-2">
              <button
                onClick={handleFitToWidth}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  fitMode === 'width' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200'
                }`}
                title="Fit to Width"
              >
                Fit Width
              </button>
              <button
                onClick={handleFitToPage}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  fitMode === 'page' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200'
                }`}
                title="Fit to Page"
              >
                100%
              </button>
            </div>

            {/* Print Button */}
            <button
              onClick={handlePrint}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
              title="Print PDF"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
            </button>

            {/* Download Button */}
            <button
              onClick={handleDownload}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
              title="Download PDF"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 9a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>

            {/* Rotate Button */}
            <button
              onClick={handleRotate}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
              title="Rotate 90° (R)"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            {/* Zoom Controls */}
            <div className="flex items-center space-x-1 border border-gray-300 rounded">
              <button
                onClick={handleZoomOut}
                disabled={scale <= 0.5}
                className="p-1 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Zoom Out (-)"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </button>
              <span className="px-2 text-xs text-gray-600 bg-gray-50 border-x border-gray-300 min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                disabled={scale >= 3.0}
                className="p-1 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Zoom In (+)"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>

            {/* Fullscreen Button */}
            <button
              onClick={handleFullscreen}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
              title={isFullscreen ? "Exit Fullscreen (Esc)" : "Fullscreen (F)"}
            >
              {isFullscreen ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              )}
            </button>

            {/* Alternative Fullscreen Button */}
            <button
              onClick={handleAlternativeFullscreen}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
              title="Enhanced Fullscreen Viewer"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>

        {/* Page Navigation */}
        {numPages > 1 && (
          <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
            <button
              onClick={handlePreviousPage}
              disabled={currentPage <= 1}
              className="flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
            
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Page</span>
              <input
                type="number"
                min="1"
                max={numPages}
                value={currentPage}
                onChange={(e) => {
                  const page = parseInt(e.target.value);
                  if (page >= 1 && page <= numPages) {
                    setCurrentPage(page);
                  }
                }}
                className="w-16 px-2 py-1 text-sm border border-gray-300 rounded text-center"
              />
              <span className="text-sm text-gray-600">of {numPages}</span>
            </div>
            
            <button
              onClick={handleNextPage}
              disabled={currentPage >= numPages}
              className="flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* PDF Viewer */}
        <div className="flex-1 bg-gray-100" id="pdf-container" style={{overflow: 'auto', display: 'block'}}>
          <div className="p-4" style={{display: 'flex', justifyContent: 'center', minWidth: '100%'}}>
            {pdfData && (
              <Document
                file={pdfData}
                onLoadSuccess={onDocumentLoadSuccess}
                onLoadError={onDocumentLoadError}
                style={{display: 'inline-block'}}
                loading={
                  <div className="flex flex-col items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-gray-600">Loading PDF...</p>
                    <p className="text-xs text-gray-500 mt-2">Please wait while we decrypt and load your document</p>
                  </div>
                }
                error={
                  <div className="flex flex-col items-center justify-center h-64 text-red-500">
                    <svg className="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-semibold">Failed to load PDF</p>
                    <p className="text-sm text-gray-600 mt-1">The document may be corrupted or invalid</p>
                  </div>
                }
              >
                <div className="shadow-lg border border-gray-300 bg-white rounded" style={{display: 'inline-block'}}>
                  <Page
                    pageNumber={currentPage}
                    scale={scale}
                    rotate={rotation}
                    onLoadSuccess={onPageLoadSuccess}
                    loading={
                      <div className="flex items-center justify-center h-96 bg-gray-50">
                        <div className="animate-pulse text-gray-500">Loading page {currentPage}...</div>
                      </div>
                    }
                    error={
                      <div className="flex items-center justify-center h-96 bg-red-50 text-red-500">
                        <div className="text-center">
                          <p className="font-semibold">Error loading page {currentPage}</p>
                          <p className="text-sm text-gray-600 mt-1">Try refreshing or selecting a different page</p>
                        </div>
                      </div>
                    }
                  />
                </div>
              </Document>
            )}
          </div>
        </div>
      </div>

      {/* Keyboard shortcuts help */}
      {isFullscreen && (
        <div className="absolute bottom-4 right-4 bg-black bg-opacity-75 text-white text-xs p-2 rounded">
          <p>Keyboard shortcuts:</p>
          <p>← → Navigate pages | + - Zoom | R Rotate | F Fullscreen | T ToC | Esc Exit</p>
        </div>
      )}

      {/* Alternative Fullscreen Viewer */}
      {showAlternativeFullscreen && (
        <FullscreenPDFViewer
          fileData={fileData || offlineData}
          filename={filename}
          initialPage={currentPage}
          onClose={() => setShowAlternativeFullscreen(false)}
          autoHideControls={true}
          theme="dark"
        />
      )}
    </div>
  );
}