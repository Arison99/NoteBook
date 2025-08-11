import React, { useState, useEffect } from 'react';
import { OfflineStorage } from '../utils/offlineStorage';

export default function OfflineIndicator({ pdfId, pdfData, filename, onCacheChange }) {
  const [isCached, setIsCached] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [cacheInfo, setCacheInfo] = useState(null);

  useEffect(() => {
    checkCacheStatus();
  }, [pdfId]);

  const checkCacheStatus = async () => {
    if (!pdfId) return;
    
    try {
      const cachedData = await OfflineStorage.getCachedPDF(pdfId);
      setIsCached(!!cachedData);
      setCacheInfo(cachedData);
    } catch (error) {
      console.error('Error checking cache status:', error);
      setIsCached(false);
    }
  };

  const handleCacheToggle = async () => {
    if (!pdfId) return;
    
    setIsLoading(true);
    try {
      if (isCached) {
        // Remove from cache
        const success = await OfflineStorage.removeCachedPDF(pdfId);
        if (success) {
          setIsCached(false);
          setCacheInfo(null);
          onCacheChange && onCacheChange(false);
        }
      } else {
        // Add to cache
        if (pdfData && filename) {
          const success = await OfflineStorage.cachePDF(pdfId, pdfData, filename);
          if (success) {
            setIsCached(true);
            await checkCacheStatus();
            onCacheChange && onCacheChange(true);
          }
        } else {
          console.warn('No PDF data available to cache');
        }
      }
    } catch (error) {
      console.error('Error toggling cache:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return 'Unknown size';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    if (mb >= 1) {
      return `${mb.toFixed(1)} MB`;
    }
    return `${kb.toFixed(1)} KB`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return '';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={handleCacheToggle}
        disabled={isLoading || !pdfData}
        className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
          isCached
            ? 'bg-green-100 text-green-700 hover:bg-green-200'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        } ${isLoading || !pdfData ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        title={
          isCached
            ? `Remove from offline storage (cached ${formatDate(cacheInfo?.cachedAt)})`
            : 'Save for offline reading'
        }
      >
        {isLoading ? (
          <svg className="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        ) : isCached ? (
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
            <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20Z" />
          </svg>
        ) : (
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 9a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        <span>
          {isLoading
            ? 'Processing...'
            : isCached
            ? 'Offline'
            : 'Cache'
          }
        </span>
      </button>

      {isCached && cacheInfo && (
        <div className="text-xs text-gray-500" title={`Cached on ${formatDate(cacheInfo.cachedAt)}`}>
          {formatSize(cacheInfo.size)}
        </div>
      )}
    </div>
  );
}
