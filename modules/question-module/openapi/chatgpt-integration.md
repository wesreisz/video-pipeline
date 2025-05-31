# ChatGPT Integration Guide

This guide explains how to integrate the Video Pipeline Question API with ChatGPT using the OpenAPI schema.

## Overview

The Question API allows ChatGPT to search through transcribed video content from QCon talks and technical presentations. Users can ask questions about specific speakers, technologies, or concepts, and ChatGPT will query the semantic search system to provide relevant answers with source attribution.

## Quick Setup

### 1. Create a Custom GPT

1. Go to [ChatGPT](https://chat.openai.com) and click "Create a GPT"
2. Configure the GPT with the following settings:

**Name**: `QCon Video Search Assistant`

**Description**: 
```
AI assistant that can search through QCon conference video transcripts to answer questions about technical talks, speakers, and topics. Provides direct quotes and source attribution from conference presentations.
```

### 2. Configure the Action

1. In the GPT configuration, go to the "Actions" section
2. Click "Create new action"
3. Import the OpenAPI schema:

**Schema Import**: Copy the entire content from [`openapi.yaml`](openapi.yaml) into the schema editor.

**Authentication**: 
- Type: `API Key`
- API Key: `YOUR_API_KEY_HERE` (format: `icaet-ak-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
- Auth Type: `Custom`
- Custom Header Name: `x-api-key`

### 3. Update Server Configuration

In the imported schema, update the server URLs to match your deployment:

```yaml
servers:
  - url: https://your-actual-api-domain.com
    description: Production environment
```

## GPT Instructions

Add these instructions to your Custom GPT:

```
You are a QCon Video Search Assistant that helps users find information from conference video transcripts.

CAPABILITIES:
- Search through transcribed QCon conference talks
- Find quotes from specific speakers
- Locate discussions about technologies, patterns, and practices
- Provide source attribution with speaker names and talk titles

USAGE GUIDELINES:
1. Always ask for the user's email address before making API calls
2. Use the queryTranscripts function to search the video database
3. Present results with clear source attribution
4. Include speaker names, talk titles, and time stamps when available
5. If multiple relevant segments are found, summarize the key points
6. Always mention that results come from QCon conference presentations

RESPONSE FORMAT:
When presenting search results, use this format:

**[Speaker Name]** - *[Talk Title]*
> "[Direct quote from transcript]"

**Time**: [start_time] - [end_time] seconds
**Track**: [conference track]
**Day**: [conference day]

LIMITATIONS:
- Only searches QCon conference content
- Requires valid email address for authorization
- Limited to 5 results per query
- Some transcript segments may have limited text due to size constraints

When users ask questions, first collect their email, then search the video database, and present the findings with proper attribution.
```

## Example Interactions

### Basic Question
**User**: "What did Martin Fowler say about microservices?"

**Assistant Response**:
> I'll search the QCon video transcripts for Martin Fowler's insights on microservices. First, I need your email address to access the system.

**User**: "user@example.com"

**Assistant**: *[Calls queryTranscripts API]* 

> Here's what Martin Fowler discussed about microservices:

> **Martin Fowler** - *Microservices: Decomposing Applications*
> > "Event-driven architecture is crucial for microservices because it enables loose coupling between services while maintaining data consistency..."
> 
> **Time**: 15.5 - 45.2 seconds  
> **Track**: Architecture  
> **Day**: Tuesday

### Technology-Specific Question
**User**: "How do speakers handle distributed transactions?"

**Assistant**: *[After getting email and calling API]*

> Several speakers at QCon discussed distributed transaction patterns:

> **Sam Newman** - *Building Microservices*
> > "When designing microservices, consider domain boundaries and avoid distributed transactions when possible. Use saga patterns instead..."
> 
> **Martin Fowler** - *Enterprise Integration Patterns*  
> > "The key to handling distributed state is to design around eventual consistency rather than ACID transactions..."

## Testing the Integration

### Test Questions to Verify Setup

1. **Speaker-specific**: "What did [Speaker Name] say about [topic]?"
2. **Technology-focused**: "How do you implement [pattern/technology]?"
3. **General concepts**: "What are the best practices for [architecture pattern]?"

### Expected Behavior

✅ **Correct**:
- Asks for email address before API calls
- Provides direct quotes with attribution
- Includes time stamps and talk details
- Handles multiple results appropriately

❌ **Issues to Check**:
- API key authentication errors
- Email authorization failures
- Missing source attribution
- Incomplete response formatting

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API key format: `icaet-ak-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - Check that key is set in Custom Header as `x-api-key`
   - Ensure API key is active and not expired

2. **Authorization Failures**
   - Confirm user email is in the authorized access list
   - Check email format is valid
   - Verify access list is properly deployed

3. **No Results Found**
   - Try more specific questions
   - Include speaker names when known
   - Use technical terminology from the conference domain

4. **Schema Import Issues**
   - Ensure complete YAML is copied without truncation
   - Validate YAML syntax using the validation script
   - Check that all required sections are present

### API Endpoint Verification

Test the API directly to verify it's working:

```bash
curl -X POST "https://your-api-domain.com/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: icaet-ak-your-key-here" \
  -d '{"question": "test question", "email": "test@example.com"}'
```

## Customization Options

### Modify Search Behavior

Update the GPT instructions to:
- Focus on specific conference tracks
- Prioritize certain speakers
- Filter by conference days
- Emphasize particular topics

### Enhanced Responses

Consider adding:
- Links to full video recordings (if available)
- Related talk recommendations
- Speaker biography information
- Conference session details

## Support

For technical issues:
- Check the [API Documentation](README.md)
- Review [OpenAPI Schema](openapi.yaml) 
- Run the [validation script](../scripts/validate-openapi.py)
- Contact system administrators for API key issues

For ChatGPT-specific issues:
- Refer to [OpenAI's Custom GPT documentation](https://help.openai.com/en/articles/8554397-creating-a-gpt)
- Check the Actions configuration in your GPT settings
- Verify the schema import was successful 