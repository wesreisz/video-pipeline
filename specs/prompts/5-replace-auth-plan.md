# GitHub OAuth Implementation - LLM-Assisted Development Prompts

Here's a breakdown of the implementation into sequential, actionable prompts you can use with an LLM:

## Phase 1: Foundation - Data Models and Feature Flags

### Prompt 1: Create Authentication Data Models
```
I need to create data models for the GitHub OAuth authentication system. 

Please create a file `modules/question-module/src/models/auth_models.py` that includes:

1. An `AuthMethod` enum with values: API_KEY, COGNITO_JWT
2. An `AuthMode` enum with values: API_KEY, DUAL, COGNITO  
3. A `CognitoUser` dataclass with fields: user_id, email, github_username, github_id, name
4. An `AuthResult` dataclass with fields: is_authenticated, user_info, auth_method_used, error_message
5. A `FeatureFlags` dataclass with fields: auth_mode, auth_priority, github_access_enabled, email_access_enabled, cognito_fallback_enabled

Follow the existing codebase patterns in the question-module and include proper type hints and docstrings.
```

### Prompt 2: Create Feature Flag Service
```
I need a feature flag service that integrates with AWS Secrets Manager for runtime configuration.

Please create `modules/question-module/src/services/feature_flag_service.py` that:

1. Extends the existing secrets management pattern from `utils/secrets.py`
2. Includes a `FeatureFlagService` class that:
   - Loads feature flags from the existing secrets service
   - Has methods: `get_auth_mode()`, `is_cognito_enabled()`, `is_github_access_enabled()`, `should_fallback_to_api_key()`
   - Implements caching similar to the existing secrets pattern
   - Defaults to safe values (API_KEY mode) if flags are unavailable
   - Uses the `FeatureFlags` dataclass from auth_models

The service should integrate with the existing `SecretsService` and follow the same initialization patterns.
```

### Prompt 3: Update Requirements and Dependencies
```
I need to add JWT validation libraries to support Cognito token validation.

Please update `modules/question-module/requirements.txt` to add:
- PyJWT>=2.8.0
- cryptography>=41.0.0
- python-jose[cryptography]>=3.3.0

Ensure the additions are compatible with the existing dependencies and follow the same formatting/commenting style as the current file.
```

## Phase 2: Authentication Services

### Prompt 4: Create Cognito Service for JWT Validation
```
I need a service to handle Cognito JWT token validation and user information extraction.

Please create `modules/question-module/src/services/cognito_service.py` that:

1. Includes a `CognitoService` class with methods:
   - `validate_jwt_token(token: str) -> Optional[CognitoUser]`: Validates JWT and returns user info
   - `extract_github_username(claims: Dict) -> str`: Extracts GitHub username from JWT claims  
   - `get_user_info(token: str) -> Dict[str, Any]`: Returns ChatGPT-compatible user info format

2. Uses the existing secrets service pattern to get Cognito configuration:
   - COGNITO_USER_POOL_ID
   - COGNITO_APP_CLIENT_ID
   - COGNITO_REGION (default to us-east-1)

3. Handles JWT validation errors gracefully and follows the existing error handling patterns
4. Uses the `CognitoUser` model from auth_models
5. Includes proper logging using the existing logger pattern

Reference the existing `services/question_service.py` for the service pattern and `utils/secrets.py` for configuration management.
```

### Prompt 5: Create GitHub Authorization Utility
```
I need a utility to handle GitHub username-based authorization similar to the existing email authorization.

Please create `modules/question-module/src/utils/github_auth_util.py` that:

1. Includes a `GitHubAuthUtil` class that mirrors the pattern in `utils/auth_util.py` but for GitHub usernames
2. Has methods:
   - `is_github_username_authorized(username: str) -> bool`
   - `_load_github_access_list() -> None` 
   - `refresh_github_access_list() -> None`

3. Uses S3 to load GitHub username access lists (similar to email access lists)
4. Implements the same caching pattern (5-minute TTL) as the existing AuthUtil
5. Gets the GitHub access list URL from secrets: `github_access_list_url`
6. Follows the exact same error handling and logging patterns as the existing AuthUtil

Copy the structure and patterns from `utils/auth_util.py` but adapt for GitHub usernames instead of emails.
```

## Phase 3: Authentication Router

### Prompt 6: Create Authentication Router
```
I need a smart authentication router that can detect and route between API key and Cognito JWT authentication.

Please create `modules/question-module/src/utils/auth_router.py` that:

1. Includes an `AuthRouter` class with methods:
   - `route_authentication(headers: Dict, feature_flags: FeatureFlags) -> AuthResult`
   - `detect_auth_method(headers: Dict) -> AuthMethod`
   - `_validate_api_key(headers: Dict) -> AuthResult`
   - `_validate_cognito_jwt(headers: Dict) -> AuthResult`
   - `_handle_dual_mode_fallback(headers: Dict) -> AuthResult`

2. Logic for smart routing:
   - Detects `x-api-key` header for API key authentication
   - Detects `Authorization: Bearer` header for JWT authentication
   - Respects feature flag `auth_mode` settings
   - Implements fallback logic in dual mode

3. Uses the existing validation patterns from `question_handler.py`
4. Integrates with `CognitoService`, existing API key validation, and both authorization utilities
5. Returns `AuthResult` objects with proper error messages
6. Follows the existing error handling and logging patterns

Reference the current authentication logic in `handlers/question_handler.py` lines 63-70 and 289-297.
```

## Phase 4: Enhanced Core Services

### Prompt 7: Update Secrets Service for New Configuration
```
I need to enhance the existing secrets service to support Cognito and feature flag configuration.

Please update `modules/question-module/src/utils/secrets.py` to add these new methods to the `SecretsService` class:

1. `get_feature_flags() -> Dict[str, Any]`: Returns feature flag configuration
2. `get_cognito_user_pool_id() -> Optional[str]`: Returns Cognito User Pool ID
3. `get_cognito_app_client_id() -> Optional[str]`: Returns Cognito App Client ID  
4. `get_cognito_region() -> str`: Returns Cognito region (default: us-east-1)
5. `get_github_access_list_url() -> Optional[str]`: Returns GitHub access list S3 URL

Follow the exact same pattern as existing methods like `get_api_key()` and `get_access_list_url()`. Maintain all existing functionality and patterns.
```

### Prompt 8: Update Authentication Utility for Dual Authorization
```
I need to enhance the existing AuthUtil to support both email and GitHub username authorization.

Please update `modules/question-module/src/utils/auth_util.py` to:

1. Add a new method `is_user_authorized(identifier: str, auth_method: AuthMethod) -> bool` that:
   - Routes to email authorization for API_KEY method
   - Routes to GitHub username authorization for COGNITO_JWT method
   - Uses the existing `is_authorized()` method for email
   - Integrates with `GitHubAuthUtil` for GitHub usernames

2. Add initialization of `GitHubAuthUtil` in the `__init__` method
3. Maintain all existing functionality unchanged
4. Follow the same patterns and error handling as existing code

Only add new functionality - do not modify existing methods to ensure backward compatibility.
```

## Phase 5: Handler Integration

### Prompt 9: Update Main Lambda Handler
```
I need to update the main Lambda handler to use the new dual authentication system while maintaining backward compatibility.

Please update `modules/question-module/src/handlers/question_handler.py` to:

1. Replace the direct `validate_api_key()` call with the new `AuthRouter`
2. Update the authorization check to use the enhanced `AuthUtil.is_user_authorized()`
3. Add feature flag initialization using `FeatureFlagService`
4. Support both email (for API key) and GitHub username (for JWT) authorization
5. Maintain all existing error handling and response patterns
6. Keep the same function signatures and behavior for backward compatibility

Focus on the `lambda_handler()` function (lines 249-287) and the validation functions. The changes should be minimal and non-breaking.

Current authentication flow in lines 263-268 should be replaced with the new router, but maintain the same error response patterns.
```

## Phase 6: Infrastructure Foundation

### Prompt 10: Create Cognito Terraform Variables
```
I need to add Cognito-related variables to the Terraform question module.

Please update `infra/modules/question-module/variables.tf` to add:

1. `enable_cognito` variable (bool, default false) - Controls Cognito resource deployment
2. `github_client_id` variable (string, sensitive) - GitHub OAuth client ID
3. `github_client_secret` variable (string, sensitive) - GitHub OAuth client secret
4. `cognito_domain_prefix` variable (string) - Cognito domain prefix for OAuth endpoints

Follow the existing variable patterns and formatting in the file. Include proper descriptions and type constraints.
```

### Prompt 11: Create Conditional Cognito Infrastructure
```
I need to create conditional Cognito resources that only deploy when enabled.

Please create `infra/modules/question-module/cognito.tf` that includes:

1. Conditional Cognito User Pool (only when `var.enable_cognito` is true)
2. GitHub Identity Provider configuration for the User Pool  
3. Cognito App Client for ChatGPT integration
4. Cognito Domain for OAuth endpoints
5. IAM policy for Lambda to access Cognito (conditional)

Use the Terraform configuration from the user story specification (lines 339-370) as reference, but make all resources conditional on `var.enable_cognito`.

Follow the existing Terraform patterns in `main.tf` and use proper resource naming conventions.
```

### Prompt 12: Update Lambda Environment Variables
```
I need to update the Lambda configuration to include Cognito environment variables when enabled.

Please update `infra/modules/question-module/main.tf` to:

1. Add conditional environment variables to the Lambda function:
   - COGNITO_USER_POOL_ID (only when Cognito enabled)
   - COGNITO_APP_CLIENT_ID (only when Cognito enabled)
   - COGNITO_REGION (only when Cognito enabled)

2. Add conditional IAM policy attachment for Cognito access
3. Maintain all existing configuration unchanged

Use Terraform conditional expressions to only set these when `var.enable_cognito` is true. Follow the existing patterns for environment variables and IAM policies.
```

## Phase 7: Configuration and Testing

### Prompt 13: Create GitHub Access List Template
```
I need to create a GitHub username access list template file.

Please create `modules/question-module/access-list/github_access.csv` with:

1. A header row explaining the format
2. A few example GitHub usernames (use placeholder names)
3. The same CSV format as the existing email access list
4. Comments explaining how to add/remove users

Reference the existing email access list format if available, or create a simple CSV with one username per line.
```

### Prompt 14: Update Environment Configuration
```
I need to update the development environment configuration to support the new Cognito variables.

Please update `infra/environments/dev/main.tf` to:

1. Add the new variables to the question_module call:
   - enable_cognito = false (default to disabled)
   - github_client_id and github_client_secret as variables
   - cognito_domain_prefix

2. Add these as new variables in `infra/environments/dev/variables.tf`
3. Maintain all existing configuration unchanged

Follow the existing patterns for module calls and variable definitions.
```

## Phase 8: Documentation and Verification

### Prompt 15: Create Migration Guide and Documentation
```
I need comprehensive documentation for the new dual authentication feature.

Please create a `modules/question-module/OAUTH_MIGRATION.md` file that includes:

1. **Overview** of the dual authentication approach
2. **Feature Flag Configuration** examples and options
3. **Migration Steps** for gradual rollout
4. **API Usage Examples** for both authentication methods
5. **Rollback Procedures** for emergency situations
6. **Troubleshooting Guide** for common issues

Use the deployment strategy from the user story (lines 275-296) and include practical examples of:
- Setting feature flags in AWS Secrets Manager
- Testing both authentication methods
- Converting from API key to OAuth authentication
```

### Prompt 16: Create Validation Script
```
I need a validation script to test the dual authentication functionality.

Please create `modules/question-module/scripts/validate_auth.py` that:

1. Tests API key authentication (existing behavior)
2. Tests JWT authentication (when Cognito is enabled)
3. Tests feature flag switching between modes
4. Validates both email and GitHub username authorization
5. Tests fallback behavior in dual mode

The script should:
- Use the existing API endpoint
- Test various authentication scenarios
- Provide clear pass/fail results
- Include error handling and informative output

Reference the existing patterns in other test scripts if available.
```

## Execution Notes:

**Sequential Execution**: Execute these prompts in order, as later prompts depend on components created in earlier ones.

**Verification Points**: After every 2-3 prompts, test the components to ensure they integrate properly.

**Rollback Strategy**: Each prompt creates or modifies specific files, making it easy to revert individual changes if needed.

**Environment Setup**: Start with `enable_cognito=false` to test the feature flag system without requiring Cognito resources.

**Testing Approach**: Use the existing development environment to test each component as it's implemented.

This breakdown allows you to implement the OAuth feature incrementally, testing each component before moving to the next, while maintaining full backward compatibility throughout the process.
