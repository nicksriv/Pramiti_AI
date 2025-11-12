# Agent Creation Guide - Enhanced Features

## Overview
The agent creation system has been significantly enhanced to support organizational hierarchy, reporting relationships, and document-based role customization.

## New Features

### 1. **Reportee Role Selection**
When creating a new agent, you must select the agent's own role (reportee role) from a dropdown populated with all available roles in the system.

- **Purpose**: Defines the agent's position and responsibilities in the organization
- **Hierarchy Levels**: 
  - Level 1: CEO / Executive Director
  - Level 2: Senior Manager
  - Level 3: Manager
  - Level 4: Specialist / Subject Matter Expert
  - Level 5: Analyst
  - Level 6: Operator

### 2. **Reporting Manager Role Selection**
After selecting the reportee role, you must choose which role the agent reports to.

- **Automatic Filtering**: The dropdown only shows roles that are higher in the hierarchy (lower level number)
- **Example**: An Analyst (Level 5) can report to:
  - Specialist (Level 4)
  - Manager (Level 3)
  - Senior Manager (Level 2)
  - CEO (Level 1)

- **Validation**: The system prevents invalid reporting structures where a lower-level role reports to a higher-level role

### 3. **Document Upload for Responsibilities**
You can now upload a document (.docx, .pdf, or .txt) containing detailed job responsibilities.

#### Supported File Formats:
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format
- **TXT**: Plain text files

#### How It Works:
1. The system extracts text from the uploaded document
2. Content is appended to the base responsibilities defined by the role
3. The combined responsibilities are used to create a more detailed system prompt for the AI agent
4. This enables agents to have both standardized role responsibilities AND custom, specialized duties

#### Benefits:
- **Customization**: Each agent can have unique responsibilities beyond the standard role definition
- **Documentation**: Maintain formal job descriptions as documents
- **Flexibility**: Update agent responsibilities by uploading new documents
- **Knowledge Base**: The document content becomes part of the agent's context

## Creating a New Agent - Step by Step

### Step 1: Click "Add Agent"
Navigate to the Agents tab and click the "Add Agent" button in the top right corner.

### Step 2: Fill in Basic Information
- **Agent Name**: Enter a descriptive name (e.g., "Security Analyst", "Database Administrator")
- **Agent Type**: Specify the functional area (e.g., "Security", "ITSM", "Analytics")

### Step 3: Select Reportee Role
Choose the role that this agent will fulfill from the dropdown. This determines:
- Base responsibilities
- Permission level
- Hierarchy position

### Step 4: Select Reporting Manager Role
Choose which role this agent reports to. The system will:
- Only show roles higher in the hierarchy
- Ensure valid reporting relationships
- Display "No higher roles available" for top-level positions (CEO)

### Step 5: Specify Specialization
Enter the agent's area of expertise (e.g., "Cybersecurity and Threat Analysis", "Database Performance Optimization")

### Step 6: Choose AI Model (Optional)
Select between:
- **GPT-4o Mini**: Faster, more cost-effective (default)
- **GPT-4o**: More powerful, better for complex tasks

### Step 7: Upload Responsibilities Document (Optional)
Click "Choose File" and upload a document containing:
- Detailed job responsibilities
- Specific tasks and duties
- Required competencies
- Performance expectations
- Any other relevant information

The file preview will show the filename once uploaded. You can remove it by clicking the "Remove" button.

### Step 8: Create Agent
Click "Create Agent" to finalize. The system will:
1. Validate all inputs
2. Process the uploaded document (if any)
3. Create the agent with combined responsibilities
4. Add hierarchy information to the agent's system prompt
5. Enable the agent in the organization

## Organizational Hierarchy

### How Hierarchy Works:
- Each agent stores its `reporting_manager_role` in metadata
- The `/api/v1/agents/hierarchy` endpoint provides the complete organizational structure
- Agents know their position and who they report to
- This enables:
  - Proper escalation paths
  - Chain of command
  - Organizational charts
  - Role-based workflows

### Hierarchy Visualization:
The Hierarchy Builder tab will display:
- CEO at the top
- Managers below
- Specialists at the bottom
- Reporting lines connecting agents to their managers

## API Endpoints

### Create Agent with Document Upload
```http
POST /agents
Content-Type: multipart/form-data

Fields:
- name: string (required)
- agent_type: string (required)
- role: string (required)
- reporting_manager_role: string (optional, required for non-CEO)
- specialization: string (required)
- model: string (default: "gpt-4o-mini")
- responsibilities_doc: file (optional)
```

### Get Agent Hierarchy
```http
GET /api/v1/agents/hierarchy

Response:
{
  "ceo": [...],
  "managers": [...],
  "specialists": [...],
  "reporting_structure": {
    "agent_id": "reporting_manager_role"
  }
}
```

## Example Use Cases

### Use Case 1: Security Team
```
CEO (Level 1)
└── Senior Security Manager (Level 2) - Reports to: CEO
    └── Security Analyst (Level 4) - Reports to: Senior Security Manager
        Upload: "Security_Analyst_Responsibilities.docx"
```

### Use Case 2: ITSM Team
```
CEO (Level 1)
└── ITSM Operations Manager (Level 2) - Reports to: CEO
    ├── Incident Manager (Level 3) - Reports to: ITSM Operations Manager
    │   └── Incident Response Specialist (Level 4) - Reports to: Incident Manager
    │       Upload: "Incident_Response_Playbook.docx"
    └── Problem Manager (Level 3) - Reports to: ITSM Operations Manager
        └── Problem Analysis Expert (Level 4) - Reports to: Problem Manager
            Upload: "Problem_Analysis_Guidelines.pdf"
```

## Sample Responsibilities Document

See `sample_responsibilities.txt` for an example of what to include in a responsibilities document.

Key sections to include:
1. **Primary Responsibilities**: Main duties and tasks
2. **Additional Duties**: Secondary responsibilities
3. **Required Competencies**: Skills and knowledge needed
4. **Performance Expectations**: How success is measured
5. **Tools and Technologies**: Relevant tools the agent should know about

## Benefits of This Approach

### For Administrators:
- ✅ Clear organizational structure
- ✅ Defined reporting relationships
- ✅ Customizable agent responsibilities
- ✅ Document-based role definitions
- ✅ Easy to update and maintain

### For AI Agents:
- ✅ Better understanding of their role
- ✅ Context about reporting structure
- ✅ Detailed task guidance from documents
- ✅ Knowledge of escalation paths
- ✅ More accurate and relevant responses

### For the Organization:
- ✅ Proper hierarchy and governance
- ✅ Clear lines of authority
- ✅ Structured decision-making
- ✅ Compliance with organizational policies
- ✅ Better collaboration between agents

## Troubleshooting

### Issue: "Please select a reporting manager role"
**Solution**: Non-CEO agents must have a reporting manager. Select a higher-level role from the dropdown.

### Issue: "No higher roles available"
**Solution**: You're creating a top-level agent (CEO). This is expected. Leave the reporting manager field empty.

### Issue: Document upload failed
**Solution**: Ensure your document is in .docx, .pdf, or .txt format and is not corrupted.

### Issue: Reporting manager role validation error
**Solution**: The reporting manager role must be higher in hierarchy (lower level number) than the agent's role.

## Future Enhancements

- 📋 Multiple document uploads per agent
- 🔄 Document versioning and history
- 📊 Hierarchy visualization in dashboard
- 🔍 Search agents by reporting relationship
- 📈 Organizational chart generation
- 🔐 Role-based access control based on hierarchy
