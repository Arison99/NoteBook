import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import HomePage from './pages/HomePage';
import PDFsPage from './pages/PDFsPage';
import UploadPage from './pages/UploadPage';
import CategoriesPage from './pages/CategoriesPage';
import OfflinePage from './pages/OfflinePage';
import AnalyticsPage from './pages/AnalyticsPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/pdfs" element={<PDFsPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/offline" element={<OfflinePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
