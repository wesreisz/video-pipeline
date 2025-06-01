# User Story: GitHub OAuth Authentication Integration with ChatGPT using AWS Cognito - Dual Authentication Approach

## Story Description

**As a** system administrator and API consumer  
**I want** to integrate GitHub OAuth authentication using AWS Cognito federated identity alongside the existing API key system with feature flag controls
**So that** I can provide a modern OAuth authentication option while maintaining backward compatibility and enabling gradual migration without service disruption

## Background

The question-module currently uses:
- **API key authentication** for rate limiting and basic access control
- **Email-based authorization** via S3 access lists to determine user authorization
- **ChatGPT integration** that relies on the existing API structure

This story **extends the existing system** with **AWS Cognito User Pool configured with GitHub as a federated identity provider** while maintaining full backward compatibility. The implementation uses **feature flags** to enable gradual rollout and **zero-downtime migration** from API keys to OAuth authentication.

**Key Change**: This is now a **NON-BREAKING additive change** that allows both authentication methods to coexist.

## Requirements

### Functional Requirements

#### FR-1: Dual Authentication System with Feature Flags
- **Requirement**: Implement feature flag-controlled dual authentication supporting both API key and Cognito JWT tokens
- **Details**: 
  - Support three auth modes via feature flags: `api_key`, `cognito`, `dual`
  - Smart authentication routing based on request headers (Bearer token vs x-api-key)
  - Maintain full backward compatibility with existing API key clients
  - No changes required for existing API consumers

#### FR-2: Cognito-Based Authentication System (Additive)
- **Requirement**: Add AWS Cognito User Pool with GitHub federated identity as alternative authentication method
- **Details**: 
  - Cognito JWT tokens containing GitHub identity for new API access
  - Existing API key authentication continues unchanged
  - Users can choose between API key or GitHub OAuth authentication
  - No Cognito user credentials required - federated identity only

#### FR-3: GitHub Federated Identity Integration
- **Requirement**: Configure Cognito Identity Provider with GitHub OAuth integration
- **Details**:
  - GitHub configured as OIDC identity provider in Cognito
  - Request minimal GitHub scopes: `user:email` and `read:user`
  - Automatic user creation in Cognito upon first GitHub authentication
  - No separate GitHub OAuth implementation needed

#### FR-4: Backward-Compatible Authorization Enhancement
- **Requirement**: Extend authorization system to support both email-based and GitHub username-based access control
- **Details**:
  - Maintain existing S3-based email authorization for API key users
  - Add parallel GitHub username authorization for OAuth users
  - Support dual access lists during migration period
  - No disruption to existing authorized users

#### FR-5: Feature Flag-Controlled API Enhancement
- **Requirement**: Implement feature flag system for gradual authentication rollout
- **Authentication Modes**:
  - `api_key`: Current behavior (default) - only API key authentication
  - `dual`: Support both API key and Cognito JWT authentication
  - `cognito`: Cognito JWT authentication only (future state)
- **Feature Flag Controls**:
  - `auth_mode`: Controls which authentication methods are enabled
  - `auth_priority`: In dual mode, which auth method to try first
  - `github_access_enabled`: Enable GitHub username-based authorization
  - `email_access_enabled`: Maintain email-based authorization

#### FR-6: ChatGPT OAuth Integration via Cognito
- **Requirement**: Use Cognito's built-in OAuth 2.0 endpoints for ChatGPT custom actions
- **OAuth Endpoints** (Cognito managed):
  - `/oauth2/authorize` - Authorization endpoint for ChatGPT
  - `/oauth2/token` - Token exchange endpoint for ChatGPT
  - `/oauth2/userInfo` - User information endpoint with ChatGPT-compatible format
- **OAuth Flow**: ChatGPT → Cognito OAuth → GitHub OAuth → User Authorization → Cognito Access Token
- **Client Management**: Configure ChatGPT as Cognito app client with dynamic callback URL support

#### FR-7: ChatGPT-Compatible User Info Endpoint
- **Requirement**: Ensure `/oauth2/userInfo` endpoint returns ChatGPT-compatible user information
- **Response Format**:
  ```json
  {
    "sub": "cognito_user_id",
    "email": "user@github.email",
    "name": "GitHub Display Name",
    "github_username": "github_username",
    "github_id": "12345678"
  }
  ```

#### FR-8: Zero-Downtime Migration Support
- **Requirement**: Support seamless migration from API keys to OAuth without service interruption
- **Details**:
  - Instant rollback capability via feature flag changes
  - No API consumer coordination required during initial rollout
  - Graceful handling of authentication failures with fallback options
  - Support for mixed client environments (some using API keys, some using OAuth)

### Technical Requirements

#### TR-1: Feature Flag Infrastructure
- **Feature Flag Storage**: Store flags in AWS Secrets Manager for runtime configuration
- **Flag Evaluation**: Runtime evaluation without service restart
- **Flag Structure**:
  ```json
  {
    "auth_mode": "dual",
    "auth_priority": "cognito", 
    "github_access_enabled": true,
    "email_access_enabled": true,
    "cognito_fallback_enabled": true
  }
  ```
- **Environment Variables**:
  - `COGNITO_USER_POOL_ID` (optional - only when Cognito enabled)
  - `COGNITO_APP_CLIENT_ID` (optional - only when Cognito enabled)
  - `COGNITO_DOMAIN` (optional - only when Cognito enabled)

#### TR-2: Dual Authentication Lambda Handler
- **Authentication Router**: Smart routing based on request headers and feature flags
- **Fallback Logic**: API key fallback when Cognito authentication fails in dual mode
- **Request Compatibility**: Support both authentication headers:
  - `x-api-key`: Existing API key authentication
  - `Authorization: Bearer <jwt>`: New Cognito JWT authentication
- **User Identification**: Extract user identifier from both auth methods for logging and authorization

#### TR-3: Enhanced Authorization System
- **Dual Access Lists**: Support both email and GitHub username access control
- **Access List URLs**:
  - `access_list_url`: Existing email-based access list
  - `github_access_list_url`: New GitHub username-based access list
- **Authorization Logic**: Route authorization checks based on authentication method used
- **Migration Utilities**: Tools to convert email-based access lists to GitHub usernames

#### TR-4: Conditional Cognito Infrastructure
- **Deployment Flag**: `enable_cognito` Terraform variable to conditionally deploy Cognito resources
- **Cognito Resources** (when enabled):
  - Cognito User Pool with GitHub identity provider
  - Cognito app clients for ChatGPT and API access
  - Cognito domain for OAuth endpoints
  - GitHub OAuth application integration
- **API Gateway**: Maintain existing `authorization = "NONE"` - handle auth in Lambda
- **No API Gateway Changes**: Avoid API Gateway redeployment complexity

#### TR-5: Security Requirements
- **Fail-Safe Defaults**: Default to API key authentication if feature flags unavailable
- **Authentication Validation**: Proper JWT validation for Cognito tokens
- **Authorization Consistency**: Maintain same authorization logic regardless of auth method
- **Logging Enhancement**: Log authentication method used for audit and monitoring

### Non-Functional Requirements

#### NFR-1: Backward Compatibility
- **Zero Breaking Changes**: Existing API consumers continue working without modification
- **Performance**: No performance degradation for existing API key authentication
- **API Compatibility**: All existing API contracts maintained
- **Migration Timeline**: No forced migration timeline - clients migrate when ready

#### NFR-2: Reliability and Rollback
- **Instant Rollback**: <1 minute rollback via feature flag change
- **Fallback Reliability**: API key authentication always available as fallback
- **Error Isolation**: Cognito failures don't impact API key authentication
- **Availability**: >99.9% uptime maintained during rollout

#### NFR-3: Performance
- **Authentication Overhead**: <25ms additional latency for new auth methods
- **Smart Routing**: Efficient authentication method detection
- **Caching**: Maintain existing authorization caching strategies
- **Feature Flag Performance**: <1ms feature flag evaluation overhead

#### NFR-4: Operational Excellence
- **Monitoring**: Comprehensive metrics for both authentication methods
- **Alerting**: Separate alerts for API key vs Cognito authentication failures
- **Gradual Rollout**: Support for percentage-based user migration
- **Observability**: Clear authentication method tracking in logs and metrics

## Acceptance Criteria

### AC-1: Feature Flag System
- [ ] Feature flags stored in AWS Secrets Manager with runtime evaluation
- [ ] Support for three auth modes: `api_key`, `dual`, `cognito`
- [ ] Instant feature flag updates without service restart
- [ ] Default behavior maintains existing API key authentication

### AC-2: Dual Authentication Mode
- [ ] API requests with API key authentication work unchanged
- [ ] API requests with Bearer JWT tokens authenticate via Cognito
- [ ] Smart routing detects authentication method from request headers
- [ ] Fallback from Cognito to API key authentication when enabled
- [ ] Both authentication methods work simultaneously

### AC-3: Backward Compatibility Validation
- [ ] All existing API consumers continue working without changes
- [ ] No performance degradation for API key authentication
- [ ] Existing access lists continue to function
- [ ] No API contract changes required

### AC-4: Cognito GitHub Federation (When Enabled)
- [ ] Cognito User Pool configured with GitHub as identity provider
- [ ] Users can authenticate via GitHub through Cognito federation
- [ ] Cognito generates valid JWT tokens containing GitHub user information
- [ ] GitHub username extracted from JWT for authorization checks

### AC-5: Enhanced Authorization System
- [ ] Email-based authorization continues for API key users
- [ ] GitHub username-based authorization works for OAuth users
- [ ] Dual access lists supported during migration period
- [ ] Authorization method automatically selected based on authentication type

### AC-6: Zero-Downtime Migration
- [ ] Service remains available throughout feature flag changes
- [ ] Rollback to API key-only mode completes within 1 minute
- [ ] No coordination required with API consumers during rollout
- [ ] Mixed client environments supported (API key + OAuth simultaneously)

### AC-7: ChatGPT Integration (When Enabled)
- [ ] ChatGPT can authenticate via Cognito OAuth endpoints
- [ ] User information endpoint returns GitHub data in ChatGPT-compatible format
- [ ] OAuth callback URLs managed for ChatGPT integration
- [ ] ChatGPT custom actions work with Cognito-issued access tokens

### AC-8: Operational Monitoring
- [ ] Metrics track authentication method usage (API key vs Cognito)
- [ ] Alerts differentiate between API key and Cognito authentication failures
- [ ] Logs include authentication method for all requests
- [ ] Performance monitoring for both authentication paths

## Implementation Tasks

### Phase 1: Dual Authentication Foundation (Week 1)
- [ ] Implement feature flag system in AWS Secrets Manager
- [ ] Create authentication router with smart header detection
- [ ] Add Cognito JWT validation service (conditional on feature flags)
- [ ] Enhance authorization system for dual access list support
- [ ] Update Lambda handler for dual authentication support
- [ ] Add comprehensive logging for authentication method tracking

### Phase 2: Conditional Cognito Infrastructure (Week 1-2)
- [ ] Create conditional Cognito Terraform module with `enable_cognito` flag
- [ ] Configure GitHub OAuth application for Cognito integration
- [ ] Set up Cognito app clients for ChatGPT and API access
- [ ] Create GitHub username-based access list structure in S3
- [ ] Implement access list migration utilities
- [ ] Deploy infrastructure with Cognito disabled by default

### Phase 3: Dual Mode Testing and Validation (Week 2)
- [ ] Enable dual authentication mode via feature flags
- [ ] Test API key authentication (existing behavior)
- [ ] Test Cognito JWT authentication with GitHub usernames
- [ ] Validate fallback behavior from Cognito to API key
- [ ] Test mixed client scenarios (API key + OAuth simultaneously)
- [ ] Performance testing for both authentication paths

### Phase 4: ChatGPT Integration Testing (Week 2-3)
- [ ] Enable Cognito infrastructure via Terraform flags
- [ ] Create test ChatGPT custom action with Cognito OAuth
- [ ] Test OAuth flow end-to-end with actual ChatGPT integration
- [ ] Validate user info endpoint compatibility with ChatGPT
- [ ] Test error scenarios and fallback behaviors

### Phase 5: Production Rollout and Monitoring (Week 3)
- [ ] Deploy to production with `auth_mode="api_key"` (no behavior change)
- [ ] Enable monitoring and alerting for dual authentication metrics
- [ ] Gradual rollout: Switch to `auth_mode="dual"` for testing
- [ ] Client migration support and documentation
- [ ] Optional future migration to `auth_mode="cognito"`

## Migration Strategy

### Zero-Downtime Rollout Plan

#### Week 1: Infrastructure Preparation
```bash
# Deploy with existing behavior (no changes)
export TF_VAR_enable_cognito="false"
export AUTH_MODE="api_key"
./deploy.sh
```

#### Week 2: Enable Cognito Infrastructure
```bash
# Deploy Cognito resources (not yet used)
export TF_VAR_enable_cognito="true"
./deploy.sh

# Create GitHub access list (parallel to email list)
aws s3 cp github_access.csv s3://dev-access-list/github_access.csv
```

#### Week 3: Enable Dual Authentication
```bash
# Switch to dual mode - supports both API key and OAuth
aws secretsmanager update-secret --secret-id dev-video-pipeline-secrets \
  --secret-string '{"auth_mode": "dual", "github_access_enabled": true}'
```

#### Future: Optional Migration to OAuth
```bash
# Only when ready - no forced timeline
aws secretsmanager update-secret --secret-id dev-video-pipeline-secrets \
  --secret-string '{"auth_mode": "cognito"}'
```

### Rollback Strategy
```bash
# Instant rollback to API key only (< 1 minute)
aws secretsmanager update-secret --secret-id dev-video-pipeline-secrets \
  --secret-string '{"auth_mode": "api_key"}'
```

## Definition of Done

- [ ] All acceptance criteria are met and tested
- [ ] Zero breaking changes - all existing API consumers continue working
- [ ] Feature flag system enables instant rollback capability
- [ ] Dual authentication mode supports both API key and Cognito JWT
- [ ] GitHub username-based authorization works alongside email-based authorization
- [ ] ChatGPT integration tested and working with Cognito OAuth
- [ ] Comprehensive monitoring for both authentication methods
- [ ] Documentation updated for dual authentication approach
- [ ] Performance benchmarks show no degradation for existing API key users
- [ ] Migration utilities available for email-to-GitHub username conversion

## Configuration Requirements

### Feature Flag Configuration
```json
{
  "auth_mode": "dual",
  "auth_priority": "cognito",
  "github_access_enabled": true,
  "email_access_enabled": true,
  "cognito_fallback_enabled": true
}
```

### AWS Cognito Configuration (Conditional)
```hcl
# Terraform configuration with conditional deployment
resource "aws_cognito_user_pool" "video_pipeline" {
  count = var.enable_cognito ? 1 : 0
  
  name = "${var.environment}-video-pipeline-users"
  username_attributes = ["email"]
  auto_verified_attributes = ["email"]
}

resource "aws_cognito_identity_provider" "github" {
  count = var.enable_cognito ? 1 : 0
  
  user_pool_id  = aws_cognito_user_pool.video_pipeline[0].id
  provider_name = "GitHub"
  provider_type = "OIDC"

  provider_details = {
    client_id     = var.github_client_id
    client_secret = var.github_client_secret
    authorize_scopes = "user:email read:user"
    oidc_issuer   = "https://github.com"
    authorize_url = "https://github.com/login/oauth/authorize"
    token_url     = "https://github.com/login/oauth/access_token"
    userinfo_url  = "https://api.github.com/user"
  }

  attribute_mapping = {
    email    = "email"
    username = "login"
    name     = "name"
  }
}
```

### Dual Authentication Headers Support
```http
# Existing API key authentication (continues working)
POST /query
x-api-key: your-api-key
Content-Type: application/json

{
  "question": "Your question here",
  "email": "user@example.com"
}

# New Cognito JWT authentication  
POST /query
Authorization: Bearer cognito-jwt-token
Content-Type: application/json

{
  "question": "Your question here"
}
```

## Authentication Flow Documentation

### Dual Authentication Flow
1. **Request Received**: API Gateway forwards to Lambda (no changes)
2. **Smart Authentication Routing**:
   - Check feature flag `auth_mode`
   - If `api_key`: Use existing API key validation
   - If `dual`: Detect auth method from headers (Bearer vs x-api-key)
   - If `cognito`: Use only Cognito JWT validation
3. **Authentication Execution**:
   - API Key: Existing validation + email authorization
   - Cognito JWT: Token validation + GitHub username authorization
4. **Fallback Handling** (in dual mode):
   - If Cognito JWT fails and API key present: Fall back to API key auth
   - If both fail: Return authentication error
5. **Request Processing**: Continue with existing question processing logic

### Migration Path for API Consumers

#### Immediate (No Changes Required)
- Existing API key authentication continues working
- No code changes needed for current API consumers
- Performance unchanged

#### Optional Migration to OAuth
- Implement GitHub OAuth flow with Cognito endpoints
- Switch from `x-api-key` header to `Authorization: Bearer` header
- Update from email-based to GitHub username-based authorization
- Migrate at own pace - no forced timeline

## Dependencies

- **Existing**: AWS Services (Lambda, API Gateway, S3, Secrets Manager)
- **New (Optional)**: AWS Cognito, GitHub OAuth API
- **ChatGPT**: OAuth 2.0 client capabilities in ChatGPT custom actions
- **Development**: Access to ChatGPT Plus for testing custom actions

## Risks & Mitigations

- **Risk**: Feature flag failures affecting authentication
  - **Mitigation**: Default to API key authentication if flags unavailable
- **Risk**: Cognito service outages
  - **Mitigation**: Automatic fallback to API key authentication in dual mode
- **Risk**: Increased complexity in authentication logic
  - **Mitigation**: Comprehensive testing and monitoring for both auth paths
- **Risk**: Mixed authentication environments causing confusion
  - **Mitigation**: Clear documentation and gradual migration approach

## Success Metrics

- **Backward Compatibility**: 100% of existing API consumers continue working without changes
- **Zero Downtime**: 100% uptime during feature rollout and rollback operations
- **Performance**: <25ms additional latency for new authentication methods
- **Reliability**: <0.1% authentication failure rate for both auth methods
- **Migration Flexibility**: Support for indefinite dual authentication mode
- **Rollback Speed**: <1 minute rollback time via feature flag changes
- **Developer Experience**: No forced migration timeline - clients migrate when ready

## Complexity Assessment: MEDIUM (Reduced from HIGH)

**Reduced Complexity Factors**:
- **No Breaking Changes**: Eliminates client coordination complexity
- **Gradual Rollout**: Reduces deployment risk
- **Instant Rollback**: Minimizes failure impact
- **Additive Approach**: Builds on existing system vs. replacement

**Success Likelihood: 85% (Increased from 65%)**

**Timeline: 2-3 weeks (More realistic than aggressive 3-week complete migration)**

## Architectural Guidelines
Be sure to follow all of the guidelines and structures in:
- .cursor/rules/project-architecture.md
- .cursor/rules/project-structure.md
- .cursor/rules/pytest.md
- .cursor/rules/terraform.md