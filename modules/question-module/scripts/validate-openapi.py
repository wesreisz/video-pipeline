#!/usr/bin/env python3
"""
OpenAPI Schema Validation Script

This script validates the OpenAPI schema for the question-module API.
It checks for proper formatting, required fields, and schema compliance.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List


def load_openapi_spec(file_path: Path) -> Dict[str, Any]:
    """Load and parse the OpenAPI specification from YAML file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"OpenAPI file not found: {file_path}")
        sys.exit(1)


def validate_openapi_structure(spec: Dict[str, Any]) -> List[str]:
    """Validate the basic structure of the OpenAPI specification."""
    errors = []
    
    # Check required top-level fields
    required_fields = ['openapi', 'info', 'paths', 'components']
    for field in required_fields:
        if field not in spec:
            errors.append(f"Missing required field: {field}")
    
    # Validate OpenAPI version
    if 'openapi' in spec:
        version = spec['openapi']
        if not version.startswith('3.0'):
            errors.append(f"Unsupported OpenAPI version: {version}. Expected 3.0.x")
    
    # Validate info section
    if 'info' in spec:
        info = spec['info']
        required_info_fields = ['title', 'version', 'description']
        for field in required_info_fields:
            if field not in info:
                errors.append(f"Missing required info field: {field}")
    
    return errors


def validate_paths(spec: Dict[str, Any]) -> List[str]:
    """Validate the paths section of the OpenAPI specification."""
    errors = []
    
    if 'paths' not in spec:
        return errors
    
    paths = spec['paths']
    
    # Check if /query endpoint exists
    if '/query' not in paths:
        errors.append("Missing required /query endpoint")
        return errors
    
    query_path = paths['/query']
    
    # Check if POST method exists
    if 'post' not in query_path:
        errors.append("Missing POST method for /query endpoint")
        return errors
    
    post_method = query_path['post']
    
    # Validate required fields in POST method
    required_post_fields = ['summary', 'requestBody', 'responses', 'security']
    for field in required_post_fields:
        if field not in post_method:
            errors.append(f"Missing required field in POST /query: {field}")
    
    # Validate responses
    if 'responses' in post_method:
        responses = post_method['responses']
        required_responses = ['200', '400', '401', '500']
        for status_code in required_responses:
            if status_code not in responses:
                errors.append(f"Missing response definition for status code: {status_code}")
    
    return errors


def validate_components(spec: Dict[str, Any]) -> List[str]:
    """Validate the components section of the OpenAPI specification."""
    errors = []
    
    if 'components' not in spec:
        return errors
    
    components = spec['components']
    
    # Check for required schemas
    if 'schemas' not in components:
        errors.append("Missing schemas in components")
        return errors
    
    schemas = components['schemas']
    required_schemas = ['QuestionRequest', 'QueryResponse', 'ContentMatch', 'ErrorResponse']
    
    for schema_name in required_schemas:
        if schema_name not in schemas:
            errors.append(f"Missing required schema: {schema_name}")
    
    # Validate QuestionRequest schema
    if 'QuestionRequest' in schemas:
        question_schema = schemas['QuestionRequest']
        if 'required' not in question_schema:
            errors.append("QuestionRequest schema missing 'required' field")
        elif set(question_schema['required']) != {'question', 'email'}:
            errors.append("QuestionRequest schema should require 'question' and 'email' fields")
    
    # Check for security schemes
    if 'securitySchemes' not in components:
        errors.append("Missing securitySchemes in components")
    elif 'ApiKeyAuth' not in components['securitySchemes']:
        errors.append("Missing ApiKeyAuth security scheme")
    
    return errors


def validate_examples(spec: Dict[str, Any]) -> List[str]:
    """Validate that examples are present and well-formed."""
    errors = []
    
    # Check for request examples
    try:
        post_method = spec['paths']['/query']['post']
        request_body = post_method['requestBody']
        content = request_body['content']['application/json']
        
        if 'examples' not in content:
            errors.append("Missing request examples in /query POST method")
        else:
            examples = content['examples']
            if not examples:
                errors.append("Empty request examples in /query POST method")
    except KeyError as e:
        errors.append(f"Error accessing request examples structure: {e}")
    
    # Check for response examples
    try:
        responses = spec['paths']['/query']['post']['responses']
        success_response = responses['200']
        content = success_response['content']['application/json']
        
        if 'examples' not in content:
            errors.append("Missing response examples for 200 status")
    except KeyError as e:
        errors.append(f"Error accessing response examples structure: {e}")
    
    return errors


def main():
    """Main validation function."""
    print("🔍 Validating OpenAPI Schema for Question Module...")
    print("=" * 50)
    
    # Locate the OpenAPI file in the new location
    script_dir = Path(__file__).parent
    openapi_file = script_dir.parent / "openapi" / "openapi.yaml"
    
    if not openapi_file.exists():
        print(f"❌ OpenAPI file not found: {openapi_file}")
        sys.exit(1)
    
    print(f"📁 Loading schema: {openapi_file}")
    
    # Load and validate the specification
    spec = load_openapi_spec(openapi_file)
    
    all_errors = []
    
    # Run validation checks
    print("\n🔧 Validating OpenAPI structure...")
    all_errors.extend(validate_openapi_structure(spec))
    
    print("🔧 Validating API paths...")
    all_errors.extend(validate_paths(spec))
    
    print("🔧 Validating components...")
    all_errors.extend(validate_components(spec))
    
    print("🔧 Validating examples...")
    all_errors.extend(validate_examples(spec))
    
    # Report results
    print("\n" + "=" * 50)
    
    if all_errors:
        print("❌ Validation failed with the following errors:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        sys.exit(1)
    else:
        print("✅ OpenAPI schema validation passed!")
        print(f"   - OpenAPI version: {spec.get('openapi', 'Unknown')}")
        print(f"   - API title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"   - API version: {spec.get('info', {}).get('version', 'Unknown')}")
        print(f"   - Endpoints: {len(spec.get('paths', {}))}")
        print(f"   - Schemas: {len(spec.get('components', {}).get('schemas', {}))}")
        print("\n🎉 Schema is ready for ChatGPT integration!")


if __name__ == "__main__":
    main() 