import { gql } from '@apollo/client';

export const GET_PDFS = gql`
  query GetPDFs {
    pdfs {
      id
      filename
      category
      encrypted_data
      compressed
    }
  }
`;

export const GET_CATEGORIES = gql`
  query GetCategories {
    categories {
      id
      name
      pdf_ids
    }
  }
`;


export const CREATE_PDF = gql`
  mutation CreatePDF($filename: String!, $category: String!, $encrypted_data: String!, $compressed: Boolean!) {
    create_pdf(filename: $filename, category: $category, encrypted_data: $encrypted_data, compressed: $compressed) {
      id
      filename
      category
      encrypted_data
      compressed
    }
  }
`;


export const CREATE_CATEGORY = gql`
  mutation CreateCategory($name: String!) {
    create_category(name: $name) {
      id
      name
    }
  }
`;

export const GET_OVERVIEW_STATS = gql`
  query GetOverviewStats {
    overviewStats {
      total_pdfs
      total_categories
      total_storage_mb
      encrypted_files
      compressed_files
      compression_ratio
    }
  }
`;

export const GET_CATEGORY_DISTRIBUTION = gql`
  query GetCategoryDistribution {
    categoryDistribution {
      category
      count
    }
  }
`;

export const GET_STORAGE_BREAKDOWN = gql`
  query GetStorageBreakdown {
    storageBreakdown {
      category
      size_mb
    }
  }
`;

export const GET_RECENT_ACTIVITY = gql`
  query GetRecentActivity {
    recentActivity {
      recent_uploads
      recent_views
      active_categories
    }
  }
`;

export const GET_SYSTEM_HEALTH = gql`
  query GetSystemHealth {
    systemHealth {
      uptime_percentage
      avg_response_time_ms
      success_rate_percentage
      error_count
      last_backup_hours_ago
    }
  }
`;

export const GET_USAGE_TRENDS = gql`
  query GetUsageTrends {
    usageTrends {
      date
      uploads
      views
      downloads
    }
  }
`;
