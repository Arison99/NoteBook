import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export default function FullscreenPDFViewer({ 
  fileData, 
  filename = "document.pdf", 
  initialPage = 1,
  onClose,
  autoHideControls = true,
  theme = 'dark' // 'dark' | 'light'
}) {
  const [numPages, setNumPages] = useState(null);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [scale, setScale] = useState(1.0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rotation, setRotation] = useState(0);
  const [fitMode, setFitMode] = useState('fit-width');
  const [showControls, setShowControls] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(2000); // ms
  const [showMinimap, setShowMinimap] = useState(false);
  const [pageWidth, setPageWidth] = useState(null);
  const [pageHeight, setPageHeight] = useState(null);
  const [viewMode, setViewMode] = useState('single'); // 'single' | 'continuous' | 'dual'
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(0);
  const [showSearch, setShowSearch] = useState(false);
  
  const hideTimer = useRef(null);
  const playTimer = useRef(null);
  const containerRef = useRef(null);
  const viewerRef = useRef(null);

  // Process PDF data
  const pdfData = useMemo(() => {
    if (!fileData) return null;
    try {
      const binaryData = Uint8Array.from(atob(fileData), c => c.charCodeAt(0));
      return { data: binaryData };
    } catch (err) {
      console.error('Error processing PDF data:', err);
      setError('Invalid PDF data format');
      return null;
    }
  }, [fileData]);

  // Auto-hide controls
  useEffect(() => {
    if (!autoHideControls) return;
    
    const resetTimer = () => {
      if (hideTimer.current) clearTimeout(hideTimer.current);
      setShowControls(true);
      hideTimer.current = setTimeout(() => {
        setShowControls(false);
      }, 3000);
    };

    const handleMouseMove = () => resetTimer();
    const handleKeyPress = () => resetTimer();

    resetTimer();
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('keypress', handleKeyPress);

    return () => {
      if (hideTimer.current) clearTimeout(hideTimer.current);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keypress', handleKeyPress);
    };
  }, [autoHideControls]);

  // Calculate scale based on fit mode
  useEffect(() => {
    if (!pageWidth || !pageHeight || !containerRef.current) return;

    const container = containerRef.current;
    const containerWidth = container.clientWidth - 40;
    const containerHeight = container.clientHeight - 100; // Account for controls

    let newScale = scale;
    
    switch (fitMode) {
      case 'fit-width':
        newScale = containerWidth / pageWidth;
        break;
      case 'fit-height':
        newScale = containerHeight / pageHeight;
        break;
      case 'fit-page':
        newScale = Math.min(containerWidth / pageWidth, containerHeight / pageHeight);
        break;
      case 'actual-size':
        newScale = 1.0;
        break;
      default:
        return;
    }
    
    setScale(Math.min(Math.max(newScale, 0.25), 5.0));
  }, [fitMode, pageWidth, pageHeight]);

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying && numPages) {
      playTimer.current = setInterval(() => {
        setCurrentPage(prev => {
          if (prev >= numPages) {
            setIsPlaying(false);
            return 1;
          }
          return prev + 1;
        });
      }, playbackSpeed);
    } else {
      if (playTimer.current) clearInterval(playTimer.current);
    }

    return () => {
      if (playTimer.current) clearInterval(playTimer.current);
    };
  }, [isPlaying, numPages, playbackSpeed]);

  // Keyboard shortcuts
  const handleKeyDown = useCallback((e) => {
    if (!numPages) return;
    
    // Prevent default for handled keys
    const handledKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', 'Escape', 'f', 'F', 's', 'S', 'r', 'R', ' '];
    if (handledKeys.includes(e.key)) {
      e.preventDefault();
    }

    switch (e.key) {
      case 'ArrowLeft':
      case 'PageUp':
        setCurrentPage(prev => Math.max(1, prev - 1));
        break;
      case 'ArrowRight':
      case 'PageDown':
      case ' ':
        setCurrentPage(prev => Math.min(numPages, prev + 1));
        break;
      case 'ArrowUp':
        if (viewMode === 'continuous') {
          viewerRef.current?.scrollBy(0, -100);
        }
        break;
      case 'ArrowDown':
        if (viewMode === 'continuous') {
          viewerRef.current?.scrollBy(0, 100);
        }
        break;
      case 'Home':
        setCurrentPage(1);
        break;
      case 'End':
        setCurrentPage(numPages);
        break;
      case '+':
      case '=':
        setScale(prev => Math.min(5.0, prev * 1.2));
        setFitMode('custom');
        break;
      case '-':
        setScale(prev => Math.max(0.25, prev / 1.2));
        setFitMode('custom');
        break;
      case 'r':
      case 'R':
        setRotation(prev => (prev + 90) % 360);
        break;
      case 'f':
      case 'F':
        setFitMode(prev => {
          const modes = ['fit-width', 'fit-height', 'fit-page', 'actual-size'];
          const currentIndex = modes.indexOf(prev);
          return modes[(currentIndex + 1) % modes.length];
        });
        break;
      case 's':
      case 'S':
        setShowSearch(prev => !prev);
        break;
      case 'Escape':
        if (showSearch) {
          setShowSearch(false);
        } else {
          onClose?.();
        }
        break;
    }
  }, [numPages, viewMode, showSearch, onClose]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const onDocumentLoadSuccess = useCallback((doc) => {
    setNumPages(doc.numPages);
    setCurrentPage(initialPage);
    setIsLoading(false);
    setError(null);
  }, [initialPage]);

  const onDocumentLoadError = useCallback((error) => {
    console.error('Document load error:', error);
    setError(`Failed to load PDF: ${error.message}`);
    setIsLoading(false);
  }, []);

  const onPageLoadSuccess = useCallback((page) => {
    if (!pageWidth) {
      setPageWidth(page.originalWidth);
      setPageHeight(page.originalHeight);
    }
  }, [pageWidth]);

  // Navigation handlers
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= numPages) {
      setCurrentPage(newPage);
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(prev => !prev);
  };

  const handleSpeedChange = (speed) => {
    setPlaybackSpeed(speed);
  };

  // Search functionality
  const handleSearch = async (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      return;
    }
    
    // This is a simplified search - in a real implementation,
    // you'd use PDF.js text extraction API
    setSearchTerm(term);
    // Mock search results for demonstration
    setSearchResults([
      { page: 1, text: term },
      { page: 3, text: term },
      { page: 7, text: term }
    ]);
    setCurrentSearchIndex(0);
  };

  const navigateSearchResult = (direction) => {
    if (searchResults.length === 0) return;
    
    const newIndex = direction === 'next' 
      ? (currentSearchIndex + 1) % searchResults.length
      : (currentSearchIndex - 1 + searchResults.length) % searchResults.length;
    
    setCurrentSearchIndex(newIndex);
    setCurrentPage(searchResults[newIndex].page);
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className={`fixed inset-0 z-50 flex items-center justify-center ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
          <p className={`text-lg ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Loading PDF...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className={`fixed inset-0 z-50 flex items-center justify-center ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
        <div className="text-center max-w-md mx-auto p-8">
          <div className={`text-6xl mb-4 ${theme === 'dark' ? 'text-red-400' : 'text-red-500'}`}>⚠️</div>
          <h2 className={`text-2xl font-bold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            Failed to Load PDF
          </h2>
          <p className={`mb-6 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>{error}</p>
          <button
            onClick={onClose}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close Viewer
          </button>
        </div>
      </div>
    );
  }

  const themeClasses = {
    background: theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100',
    surface: theme === 'dark' ? 'bg-gray-800' : 'bg-white',
    text: theme === 'dark' ? 'text-white' : 'text-gray-900',
    textSecondary: theme === 'dark' ? 'text-gray-300' : 'text-gray-600',
    border: theme === 'dark' ? 'border-gray-700' : 'border-gray-300',
    button: theme === 'dark' ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300',
    buttonActive: theme === 'dark' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'
  };

  return (
    <div className={`fixed inset-0 z-50 ${themeClasses.background}`} ref={containerRef}>
      {/* Top Controls */}
      <div className={`absolute top-0 left-0 right-0 z-10 transition-all duration-300 ${
        showControls ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'
      }`}>
        <div className={`${themeClasses.surface} shadow-lg border-b ${themeClasses.border}`}>
          <div className="flex items-center justify-between p-4">
            {/* Left section - File info */}
            <div className="flex items-center space-x-4">
              <button
                onClick={onClose}
                className={`p-2 rounded-lg ${themeClasses.button} ${themeClasses.text}`}
                title="Close (Esc)"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <div>
                <h1 className={`text-lg font-semibold ${themeClasses.text} truncate max-w-xs`}>
                  {filename}
                </h1>
                {numPages && (
                  <p className={`text-sm ${themeClasses.textSecondary}`}>
                    Page {currentPage} of {numPages}
                  </p>
                )}
              </div>
            </div>

            {/* Center section - Main controls */}
            <div className="flex items-center space-x-2">
              {/* Playback controls */}
              <button
                onClick={handlePlayPause}
                className={`p-2 rounded-lg ${isPlaying ? themeClasses.buttonActive : themeClasses.button} text-white`}
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1M9 10v4a2 2 0 002 2h2a2 2 0 002-2v-4" />
                  </svg>
                )}
              </button>

              {/* Speed controls */}
              <select
                value={playbackSpeed}
                onChange={(e) => handleSpeedChange(Number(e.target.value))}
                className={`px-3 py-1 rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border`}
              >
                <option value={500}>0.5s</option>
                <option value={1000}>1s</option>
                <option value={2000}>2s</option>
                <option value={3000}>3s</option>
                <option value={5000}>5s</option>
              </select>

              {/* View mode */}
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
                className={`px-3 py-1 rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border`}
              >
                <option value="single">Single Page</option>
                <option value="continuous">Continuous</option>
                <option value="dual">Dual Page</option>
              </select>

              {/* Fit mode */}
              <select
                value={fitMode}
                onChange={(e) => setFitMode(e.target.value)}
                className={`px-3 py-1 rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border`}
              >
                <option value="fit-width">Fit Width</option>
                <option value="fit-height">Fit Height</option>
                <option value="fit-page">Fit Page</option>
                <option value="actual-size">Actual Size</option>
              </select>
            </div>

            {/* Right section - Tools */}
            <div className="flex items-center space-x-2">
              {/* Search */}
              <button
                onClick={() => setShowSearch(!showSearch)}
                className={`p-2 rounded-lg ${showSearch ? themeClasses.buttonActive : themeClasses.button} ${showSearch ? 'text-white' : themeClasses.text}`}
                title="Search (S)"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>

              {/* Minimap */}
              <button
                onClick={() => setShowMinimap(!showMinimap)}
                className={`p-2 rounded-lg ${showMinimap ? themeClasses.buttonActive : themeClasses.button} ${showMinimap ? 'text-white' : themeClasses.text}`}
                title="Minimap"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </button>

              {/* Rotation */}
              <button
                onClick={() => setRotation(prev => (prev + 90) % 360)}
                className={`p-2 rounded-lg ${themeClasses.button} ${themeClasses.text}`}
                title="Rotate (R)"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>

              {/* Zoom display */}
              <div className={`px-3 py-2 rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border text-sm`}>
                {Math.round(scale * 100)}%
              </div>
            </div>
          </div>

          {/* Search bar */}
          {showSearch && (
            <div className={`px-4 pb-4 border-t ${themeClasses.border}`}>
              <div className="flex items-center space-x-2 max-w-md">
                <input
                  type="text"
                  placeholder="Search in document..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
                  className={`flex-1 px-3 py-2 rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  autoFocus
                />
                <button
                  onClick={() => handleSearch(searchTerm)}
                  className={`px-4 py-2 rounded ${themeClasses.buttonActive} text-white`}
                >
                  Search
                </button>
                {searchResults.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => navigateSearchResult('prev')}
                      className={`p-1 rounded ${themeClasses.button} ${themeClasses.text}`}
                    >
                      ↑
                    </button>
                    <span className={`text-sm ${themeClasses.textSecondary}`}>
                      {currentSearchIndex + 1}/{searchResults.length}
                    </span>
                    <button
                      onClick={() => navigateSearchResult('next')}
                      className={`p-1 rounded ${themeClasses.button} ${themeClasses.text}`}
                    >
                      ↓
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Controls */}
      <div className={`absolute bottom-0 left-0 right-0 z-10 transition-all duration-300 ${
        showControls ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
      }`}>
        <div className={`${themeClasses.surface} shadow-lg border-t ${themeClasses.border}`}>
          <div className="flex items-center justify-between p-4">
            {/* Page navigation */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                className={`p-2 rounded-lg ${themeClasses.button} ${themeClasses.text} disabled:opacity-50`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  min="1"
                  max={numPages}
                  value={currentPage}
                  onChange={(e) => handlePageChange(parseInt(e.target.value))}
                  className={`w-16 px-2 py-1 text-center rounded ${themeClasses.surface} ${themeClasses.text} ${themeClasses.border} border`}
                />
                <span className={themeClasses.textSecondary}>of {numPages}</span>
              </div>

              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= numPages}
                className={`p-2 rounded-lg ${themeClasses.button} ${themeClasses.text} disabled:opacity-50`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Progress bar */}
            <div className="flex-1 mx-8">
              <div className={`w-full h-2 ${themeClasses.border} border rounded-full overflow-hidden`}>
                <div 
                  className="h-full bg-blue-500 transition-all duration-300"
                  style={{ width: `${(currentPage / numPages) * 100}%` }}
                />
              </div>
            </div>

            {/* Theme toggle */}
            <button
              onClick={() => {}}
              className={`p-2 rounded-lg ${themeClasses.button} ${themeClasses.text}`}
              title="Toggle Theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </div>

      {/* Main PDF Viewer */}
      <div 
        className="absolute inset-0 overflow-auto"
        ref={viewerRef}
        style={{ 
          paddingTop: showControls ? '120px' : '20px',
          paddingBottom: showControls ? '100px' : '20px'
        }}
      >
        <div className="flex justify-center min-h-full p-4">
          {pdfData && (
            <Document
              file={pdfData}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
              }
            >
              {viewMode === 'continuous' ? (
                // Continuous view - render all pages
                Array.from(new Array(numPages), (el, index) => (
                  <div key={`page_${index + 1}`} className="mb-4">
                    <Page
                      pageNumber={index + 1}
                      scale={scale}
                      rotate={rotation}
                      onLoadSuccess={onPageLoadSuccess}
                      className="shadow-lg"
                    />
                  </div>
                ))
              ) : viewMode === 'dual' ? (
                // Dual page view
                <div className="flex space-x-4">
                  {[currentPage, currentPage + 1].map(pageNum => (
                    pageNum <= numPages && (
                      <Page
                        key={`page_${pageNum}`}
                        pageNumber={pageNum}
                        scale={scale}
                        rotate={rotation}
                        onLoadSuccess={onPageLoadSuccess}
                        className="shadow-lg"
                      />
                    )
                  ))}
                </div>
              ) : (
                // Single page view
                <Page
                  pageNumber={currentPage}
                  scale={scale}
                  rotate={rotation}
                  onLoadSuccess={onPageLoadSuccess}
                  className="shadow-lg"
                />
              )}
            </Document>
          )}
        </div>
      </div>

      {/* Minimap */}
      {showMinimap && numPages && (
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 z-20">
          <div className={`${themeClasses.surface} rounded-lg shadow-lg p-2 max-h-96 overflow-y-auto`}>
            <div className="grid grid-cols-1 gap-1" style={{ width: '80px' }}>
              {Array.from(new Array(numPages), (el, index) => {
                const pageNum = index + 1;
                const isCurrentPage = pageNum === currentPage;
                return (
                  <div
                    key={pageNum}
                    className={`relative cursor-pointer border-2 transition-all ${
                      isCurrentPage 
                        ? 'border-blue-500 bg-blue-100' 
                        : `border-transparent ${themeClasses.button}`
                    }`}
                    onClick={() => handlePageChange(pageNum)}
                    title={`Page ${pageNum}`}
                  >
                    <div className="aspect-[8.5/11] bg-white flex items-center justify-center text-xs text-gray-600">
                      {pageNum}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Keyboard shortcuts help (bottom right) */}
      <div className={`absolute bottom-20 right-4 z-20 ${themeClasses.surface} rounded-lg shadow-lg p-3 text-xs ${themeClasses.text} transition-all duration-300 ${
        showControls ? 'opacity-75' : 'opacity-0 pointer-events-none'
      }`}>
        <div className="space-y-1">
          <div><kbd>←/→</kbd> Navigate pages</div>
          <div><kbd>+/-</kbd> Zoom in/out</div>
          <div><kbd>R</kbd> Rotate</div>
          <div><kbd>F</kbd> Cycle fit modes</div>
          <div><kbd>S</kbd> Search</div>
          <div><kbd>Space</kbd> Next page</div>
          <div><kbd>Esc</kbd> Close viewer</div>
        </div>
      </div>
    </div>
  );
}