import localforage from 'localforage';

// Configure localforage for PDF storage
const pdfStorage = localforage.createInstance({
  name: 'NoteBookPDFs',
  storeName: 'pdfs',
  description: 'Offline PDF storage for NoteBook app'
});

const tocStorage = localforage.createInstance({
  name: 'NoteBookToC',
  storeName: 'toc',
  description: 'Table of Contents storage for PDFs'
});

export class OfflineStorage {
  static async cachePDF(pdfId, pdfData, filename) {
    try {
      const cacheData = {
        data: pdfData,
        filename,
        cachedAt: new Date().toISOString(),
        size: pdfData.length
      };
      await pdfStorage.setItem(pdfId, cacheData);
      console.log(`PDF ${pdfId} cached successfully`);
      return true;
    } catch (error) {
      console.error('Error caching PDF:', error);
      return false;
    }
  }

  static async getCachedPDF(pdfId) {
    try {
      const cachedData = await pdfStorage.getItem(pdfId);
      if (cachedData) {
        console.log(`PDF ${pdfId} loaded from cache`);
        return cachedData;
      }
      return null;
    } catch (error) {
      console.error('Error loading cached PDF:', error);
      return null;
    }
  }

  static async removeCachedPDF(pdfId) {
    try {
      await pdfStorage.removeItem(pdfId);
      await tocStorage.removeItem(pdfId);
      console.log(`PDF ${pdfId} removed from cache`);
      return true;
    } catch (error) {
      console.error('Error removing cached PDF:', error);
      return false;
    }
  }

  static async getCacheSize() {
    try {
      const keys = await pdfStorage.keys();
      let totalSize = 0;
      for (const key of keys) {
        const item = await pdfStorage.getItem(key);
        if (item && item.size) {
          totalSize += item.size;
        }
      }
      return totalSize;
    } catch (error) {
      console.error('Error calculating cache size:', error);
      return 0;
    }
  }

  static async clearCache() {
    try {
      await pdfStorage.clear();
      await tocStorage.clear();
      console.log('Cache cleared successfully');
      return true;
    } catch (error) {
      console.error('Error clearing cache:', error);
      return false;
    }
  }

  static async cacheToC(pdfId, outline) {
    try {
      const tocData = {
        outline,
        cachedAt: new Date().toISOString()
      };
      await tocStorage.setItem(pdfId, tocData);
      console.log(`ToC for PDF ${pdfId} cached successfully`);
      return true;
    } catch (error) {
      console.error('Error caching ToC:', error);
      return false;
    }
  }

  static async getCachedToC(pdfId) {
    try {
      const cachedToC = await tocStorage.getItem(pdfId);
      if (cachedToC) {
        console.log(`ToC for PDF ${pdfId} loaded from cache`);
        return cachedToC.outline;
      }
      return null;
    } catch (error) {
      console.error('Error loading cached ToC:', error);
      return null;
    }
  }

  static async getAllCachedPDFs() {
    try {
      const keys = await pdfStorage.keys();
      const cachedPDFs = [];
      for (const key of keys) {
        const item = await pdfStorage.getItem(key);
        if (item) {
          cachedPDFs.push({
            id: key,
            filename: item.filename,
            cachedAt: item.cachedAt,
            size: item.size
          });
        }
      }
      return cachedPDFs;
    } catch (error) {
      console.error('Error getting cached PDFs list:', error);
      return [];
    }
  }
}
