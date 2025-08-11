
# Ariadne schema for NoteBook backend
from ariadne import QueryType, MutationType, make_executable_schema, gql
from service import PDFService, CategoryService
from analytics_service import AnalyticsService

pdf_service = PDFService()
category_service = CategoryService()
analytics_service = AnalyticsService()

type_defs = gql('''
    type PDF {
        id: ID!
        filename: String!
        category: String!
        encrypted_data: String!
        compressed: Boolean!
        original_size_bytes: Int!
        compressed_size_bytes: Int!
        created_at: String!
        last_accessed: String
        access_count: Int!
    }
    type Category {
        id: ID!
        name: String!
        pdf_ids: [ID!]!
        created_at: String!
        last_modified: String!
    }
    type OverviewStats {
        total_pdfs: Int!
        total_categories: Int!
        total_storage_mb: Float!
        encrypted_files: Int!
        compressed_files: Int!
        compression_ratio: Float!
    }
    type CategoryDistribution {
        category: String!
        count: Int!
    }
    type StorageBreakdown {
        category: String!
        size_mb: Float!
    }
    type RecentActivity {
        recent_uploads: Int!
        recent_views: Int!
        active_categories: Int!
    }
    type SystemHealth {
        uptime_percentage: Float!
        avg_response_time_ms: Int!
        success_rate_percentage: Float!
        error_count: Int!
        last_backup_hours_ago: Int!
    }
    type UsageTrend {
        date: String!
        uploads: Int!
        views: Int!
        downloads: Int!
    }
    type Query {
        hello: String!
        pdfs: [PDF!]!
        categories: [Category!]!
        pdf(id: ID!): PDF
        pdfData(id: ID!): String  # Returns decrypted base64 data for viewing
        category(id: ID!): Category
        # Analytics queries
        overviewStats: OverviewStats!
        categoryDistribution: [CategoryDistribution!]!
        storageBreakdown: [StorageBreakdown!]!
        recentActivity: RecentActivity!
        systemHealth: SystemHealth!
        usageTrends: [UsageTrend!]!
    }
    type Mutation {
        create_pdf(filename: String!, category: String!, encrypted_data: String!, compressed: Boolean!): PDF!
        update_pdf(id: ID!, filename: String, category: String, encrypted_data: String, compressed: Boolean): PDF!
        delete_pdf(id: ID!): Boolean!
        create_category(name: String!): Category!
        update_category(id: ID!, name: String, pdf_ids: [ID!]): Category!
        delete_category(id: ID!): Boolean!
    }
''')

query = QueryType()
mutation = MutationType()

# Query resolvers
@query.field("hello")
def resolve_hello(*_):
    return "Hello from NoteBook backend!"

@query.field("pdfs")
def resolve_pdfs(*_):
    return pdf_service.list_pdfs()

@query.field("categories")
def resolve_categories(*_):
    return category_service.list_categories()

@query.field("pdf")
def resolve_pdf(*_, id):
    return pdf_service.get_pdf(id)

@query.field("pdfData")
def resolve_pdf_data(*_, id):
    return pdf_service.get_pdf_data(id)

@query.field("category")
def resolve_category(*_, id):
    return category_service.get_category(id)

# Analytics resolvers
@query.field("overviewStats")
def resolve_overview_stats(*_):
    return analytics_service.get_overview_stats()

@query.field("categoryDistribution")
def resolve_category_distribution(*_):
    return analytics_service.get_category_distribution()

@query.field("storageBreakdown")
def resolve_storage_breakdown(*_):
    return analytics_service.get_storage_breakdown()

@query.field("recentActivity")
def resolve_recent_activity(*_):
    return analytics_service.get_recent_activity()

@query.field("systemHealth")
def resolve_system_health(*_):
    return analytics_service.get_system_health()

@query.field("usageTrends")
def resolve_usage_trends(*_):
    return analytics_service.get_usage_trends()

# Mutation resolvers
@mutation.field("create_pdf")
def resolve_create_pdf(*_, filename, category, encrypted_data, compressed):
    # The service now handles encryption, so we pass raw data
    return pdf_service.create_pdf(filename, category, encrypted_data, should_compress=compressed)

@mutation.field("update_pdf")
def resolve_update_pdf(*_, id, filename=None, category=None, encrypted_data=None, compressed=None):
    pdf = pdf_service.get_pdf(id)
    if not pdf:
        raise Exception('PDF not found')
    if filename is not None:
        pdf['filename'] = filename
    if category is not None:
        pdf['category'] = category
    if encrypted_data is not None:
        pdf['encrypted_data'] = encrypted_data
    if compressed is not None:
        pdf['compressed'] = compressed
    pdf_service.repo.db.save(pdf)
    return pdf

@mutation.field("delete_pdf")
def resolve_delete_pdf(*_, id):
    pdf = pdf_service.get_pdf(id)
    if not pdf:
        return False
    pdf_service.repo.db.delete(pdf)
    return True

@mutation.field("create_category")
def resolve_create_category(*_, name):
    return category_service.create_category(name)

@mutation.field("update_category")
def resolve_update_category(*_, id, name=None, pdf_ids=None):
    category = category_service.get_category(id)
    if not category:
        raise Exception('Category not found')
    if name is not None:
        category['name'] = name
    if pdf_ids is not None:
        category['pdf_ids'] = pdf_ids
    category_service.repo.db.save(category)
    return category

@mutation.field("delete_category")
def resolve_delete_category(*_, id):
    category = category_service.get_category(id)
    if not category:
        return False
    category_service.repo.db.delete(category)
    return True
