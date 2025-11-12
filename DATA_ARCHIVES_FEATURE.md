# Data Archives Feature

## Overview
A comprehensive document management system for uploading, organizing, and managing organization-related documents, guidelines, policies, and reference materials. These documents can be used by AI agents to provide accurate responses and resolve tickets based on official organizational knowledge.

## Features Implemented

### 1. Data Archives Tab Navigation
- **Location**: Added between Tickets and Analytics tabs
- **Icon**: fa-archive
- **Title**: "Data Archives"

### 2. Archive Statistics Dashboard
Four stat cards showing:
- **Total Documents**: All uploaded documents
- **Guidelines**: Documents categorized as guidelines
- **Policies**: Documents categorized as policies
- **Total Size**: Combined size of all documents in MB

### 3. Document Upload Modal
Comprehensive form for uploading documents:
- **Document Title** (required): Name of the document
- **Description**: Brief description of contents
- **Category** (required): Guidelines, Policies, Procedures, Templates, Reference, Other
- **Department**: Department ownership (IT, HR, Finance, etc.)
- **File Upload** (required): Supports PDF, DOCX, TXT (Max 10MB)
- **Tags**: Comma-separated tags for organization
- **Searchable**: Toggle to make document searchable by agents

### 4. Document Filtering System
- **Category Filter**: Filter by document category
- **File Type Filter**: Filter by PDF, DOCX, or TXT
- **Search**: Text search across title, description, ID, and tags

### 5. Document List Display
Each document shows:
- **Visual Indicators**:
  - Color-coded category indicator (vertical bar)
  - File type icon (PDF, Word, Text)
  - Category badge
  
- **Metadata**:
  - Document ID (e.g., DOC-001)
  - Upload date
  - Uploader name
  - Department
  - File size
  - Searchable status indicator
  
- **Content Preview**:
  - Description
  - Tags

- **Actions**:
  - Download: Get original file
  - View: View extracted text content
  - Edit: Update metadata
  - Delete: Remove document

### 6. Backend API Endpoints

All endpoints under `/api/v1/archives`:

```
GET    /api/v1/archives              - List all documents
POST   /api/v1/archives              - Upload new document (multipart/form-data)
GET    /api/v1/archives/{id}         - Get specific document
GET    /api/v1/archives/{id}/download - Download original file
GET    /api/v1/archives/{id}/view    - View text content
PUT    /api/v1/archives/{id}         - Update document metadata
DELETE /api/v1/archives/{id}         - Delete document
GET    /api/v1/archives/search       - Search documents (for agent use)
```

### 7. Document Processing
Automatic text extraction from uploaded files:
- **TXT**: Direct UTF-8 decoding
- **DOCX**: Extracts text from Word documents using python-docx
- **PDF**: Extracts text from PDF pages using PyPDF2
- Extracted text stored for agent search and reference

### 8. Agent Integration
- Documents marked as "searchable" are available to AI agents
- Search API allows agents to query documents by keywords
- Relevance scoring prioritizes title > description > tags > content
- Returns top 10 most relevant documents

## Sample Data

The system includes 5 sample documents:

1. **DOC-001**: IT Security Policy (Policies, PDF, 2.5 MB)
   - Comprehensive IT security guidelines
   - Tags: security, IT, compliance

2. **DOC-002**: Employee Onboarding Guide (Guidelines, DOCX, 1.8 MB)
   - New employee onboarding process
   - Tags: onboarding, HR, training

3. **DOC-003**: Incident Response Procedures (Procedures, PDF, 3.2 MB)
   - Security incident handling steps
   - Tags: security, incident, procedures

4. **DOC-004**: Code of Conduct (Policies, PDF, 1.2 MB)
   - Ethics and conduct guidelines
   - Tags: ethics, conduct, policy

5. **DOC-005**: API Documentation (Reference, TXT, 0.5 MB)
   - Internal API technical reference
   - Tags: API, documentation, technical

## Color Coding by Category

- **Guidelines**: Green (#10b981)
- **Policies**: Orange/Yellow (#f59e0b)
- **Procedures**: Blue (#3b82f6)
- **Templates**: Pink (#ec4899)
- **Reference**: Purple (#a855f7)
- **Other**: Gray (#64748b)

## File Type Support

### Supported Formats
- **PDF** (.pdf): Portable Document Format
- **DOCX** (.docx): Microsoft Word Document
- **TXT** (.txt): Plain Text File

### File Size Limit
- Maximum: 10 MB per file
- Validation on both frontend and backend

### Dependencies Required
- `python-docx==1.1.0`: For DOCX processing
- `PyPDF2==3.0.1`: For PDF processing
- Already included in requirements.txt

## Use Cases

### 1. Ticket Resolution
Agents can reference organizational policies and procedures when resolving support tickets:
```
User: "What's our password policy?"
Agent searches archives → Finds "IT Security Policy" → Provides accurate answer
```

### 2. Onboarding Assistance
New employees can ask questions and get answers from official documentation:
```
User: "How do I request time off?"
Agent searches archives → Finds "Employee Handbook" → Explains process
```

### 3. Compliance Reference
Agents ensure responses align with organizational policies:
```
User: "Can I use personal email for work?"
Agent searches archives → Finds "Code of Conduct" → Provides policy-compliant answer
```

### 4. Knowledge Base
Centralized repository of organizational knowledge:
- Guidelines for standard procedures
- Templates for common documents
- Reference materials for technical teams
- Policies for governance and compliance

## Technical Implementation

### Frontend (web/enhanced-dashboard.html)
- **HTML**: Lines 3121-3226 (Archives content section)
- **HTML**: Lines 3568-3642 (Upload Document modal)
- **CSS**: Lines 6082-6265 (Archive styles)
- **JavaScript**: Lines 5344-5670 (Archive management functions)

### Backend (api_server.py)
- **Lines**: 1128-1298 (Archive endpoints)
- **Storage**: In-memory (archives_db list)
- **Processing**: Automatic text extraction
- **Search**: Relevance-based scoring

### Key JavaScript Functions
- `loadArchives()`: Fetches documents from backend or sample data
- `updateArchiveStats()`: Updates stat cards
- `filterArchives()`: Applies category, type, and search filters
- `renderArchives()`: Renders document list
- `showUploadDocumentModal()`: Opens upload modal
- `downloadDocument()`: Triggers file download
- `viewDocument()`: Opens document viewer
- `deleteDocument()`: Removes document

### Key Backend Functions
- `upload_archive()`: Handles multipart file upload and text extraction
- `get_archives()`: Returns all documents
- `search_archives()`: Agent-facing search with relevance scoring
- `download_archive()`: Serves original file
- `view_archive()`: Returns extracted text content

## Future Enhancements

1. **Database Integration**: Replace in-memory storage with MongoDB or PostgreSQL
2. **File Storage**: Use S3 or Azure Blob Storage for actual files
3. **Version Control**: Track document versions and changes
4. **Access Control**: Role-based permissions for viewing/editing
5. **Advanced Search**: Full-text search with Elasticsearch
6. **AI Summarization**: Auto-generate document summaries
7. **Related Documents**: Suggest related documents based on content
8. **Bulk Upload**: Upload multiple documents at once
9. **Document Templates**: Pre-defined templates for common document types
10. **Expiration Dates**: Set review/expiration dates for policies
11. **Approval Workflow**: Multi-step approval for sensitive documents
12. **Audit Log**: Track who viewed/downloaded each document
13. **OCR Support**: Extract text from scanned PDFs and images
14. **Collaboration**: Comments and annotations on documents
15. **Integration**: Connect with SharePoint, Google Drive, etc.

## Agent Usage Example

When an agent needs to answer a question, it can search the archives:

```python
# Agent receives question about security policy
question = "What's our password complexity requirement?"

# Search archives
response = await fetch(f"{API_BASE_URL}/api/v1/archives/search?query=password policy")
results = await response.json()

# Use top result to formulate answer
if results:
    doc = results[0]
    # Extract relevant section from doc['text_content']
    # Formulate response based on official policy
```

## Security Considerations

### Current Implementation
- File type validation (only PDF, DOCX, TXT)
- File size limit (10 MB max)
- No executable files allowed

### Production Requirements
1. **Virus Scanning**: Scan all uploads for malware
2. **Authentication**: Verify user identity before upload/access
3. **Authorization**: Role-based access control
4. **Encryption**: Encrypt files at rest and in transit
5. **Audit Trail**: Log all access and modifications
6. **Data Retention**: Implement retention policies
7. **GDPR Compliance**: Handle PII appropriately

## Testing Guide

### Manual Testing
1. **Navigate to Archives tab**
   - Click "Data Archives" in navigation
   - Verify sample documents load

2. **Upload Document**
   - Click "Upload Document" button
   - Fill in all required fields
   - Select a test file (PDF/DOCX/TXT)
   - Submit and verify success message

3. **Filter Documents**
   - Test category filter
   - Test file type filter
   - Test search functionality

4. **Document Actions**
   - View a document
   - Download a document
   - Delete a document (with confirmation)

5. **Statistics Update**
   - Verify stats update after upload
   - Verify stats update after deletion

### API Testing
```bash
# List all documents
curl http://localhost:8084/api/v1/archives

# Upload document
curl -X POST http://localhost:8084/api/v1/archives \
  -F "title=Test Document" \
  -F "category=guidelines" \
  -F "file=@test.pdf"

# Search documents
curl "http://localhost:8084/api/v1/archives/search?query=security"

# Delete document
curl -X DELETE http://localhost:8084/api/v1/archives/DOC-001
```

## Benefits

### For Users
- Easy document upload and management
- Quick search and filtering
- Centralized knowledge repository
- Consistent information source

### For Agents
- Access to authoritative information
- Ability to provide policy-compliant answers
- Reference official procedures
- Reduce hallucinations with grounded responses

### For Organization
- Single source of truth
- Improved compliance
- Better knowledge management
- Audit trail of document access
- Reduced information silos

## Notes

- Documents are currently stored in memory and will be lost on server restart
- For production, implement persistent storage (database + file storage)
- Text extraction quality depends on document format and quality
- Searchable flag allows controlling which documents agents can access
- Tags improve document discoverability
- Category-based organization helps with filtering and navigation
