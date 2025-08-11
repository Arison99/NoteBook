import React, { useState, useEffect } from 'react';

export default function TableOfContents({ outline, onNavigate, currentPage, className = "" }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedItems, setExpandedItems] = useState(new Set());

  useEffect(() => {
    // Auto-expand first level items by default
    if (outline && outline.length > 0) {
      const firstLevelItems = new Set();
      outline.forEach((item, index) => {
        if (item.items && item.items.length > 0) {
          firstLevelItems.add(index);
        }
      });
      setExpandedItems(firstLevelItems);
    }
  }, [outline]);

  const toggleExpanded = (index) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  const handleItemClick = (dest) => {
    if (dest && typeof dest.num === 'number') {
      // PDF.js destination format
      onNavigate(dest.num);
    } else if (dest && dest.page) {
      // Alternative format
      onNavigate(dest.page);
    }
  };

  const renderOutlineItem = (item, index, level = 0) => {
    const hasChildren = item.items && item.items.length > 0;
    const isExpanded = expandedItems.has(index);
    const isCurrentPage = item.dest && currentPage && 
      ((typeof item.dest.num === 'number' && item.dest.num === currentPage) ||
       (item.dest.page && item.dest.page === currentPage));

    return (
      <div key={index} className={`outline-item level-${level}`}>
        <div 
          className={`flex items-center py-1 px-2 cursor-pointer hover:bg-gray-100 rounded text-sm ${
            isCurrentPage ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-700'
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => handleItemClick(item.dest)}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleExpanded(index);
              }}
              className="mr-2 w-4 h-4 flex items-center justify-center text-gray-400 hover:text-gray-600"
            >
              {isExpanded ? (
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              ) : (
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              )}
            </button>
          )}
          <span className="flex-1 truncate" title={item.title}>
            {item.title || 'Untitled'}
          </span>
          {item.dest && (
            <span className="text-xs text-gray-400 ml-2">
              {typeof item.dest.num === 'number' ? item.dest.num : item.dest.page || '?'}
            </span>
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div className="children">
            {item.items.map((childItem, childIndex) => 
              renderOutlineItem(childItem, `${index}-${childIndex}`, level + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  if (!outline || outline.length === 0) {
    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-800">Table of Contents</h3>
        </div>
        <div className="text-center text-gray-500 py-8">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">No table of contents available</p>
          <p className="text-xs text-gray-400 mt-1">This PDF doesn't contain bookmarks or chapters</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg ${className}`}>
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-800">Table of Contents</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 text-gray-400 hover:text-gray-600 rounded"
          title={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </button>
      </div>
      
      {isExpanded && (
        <div className="max-h-96 overflow-y-auto p-2">
          {outline.map((item, index) => renderOutlineItem(item, index))}
        </div>
      )}
    </div>
  );
}
