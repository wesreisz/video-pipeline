# Prompt: AWS Lambda Python Modularization in Video Pipeline Project

## Task Description

Create a well-modularized Python AWS Lambda function within our video pipeline project that follows our established project structure and infrastructure standards. The Lambda function should be part of our transcription workflow, processing audio files from our S3 buckets. Only implement the lambda function for dev at this point
* `.cursor/rules/project-structure.md`
* `.cursor/rules/terraform.md`

## Requirements

1. Create a new Lambda function module in the appropriate project directory
2. Implement proper Python modularization following AWS Lambda best practices
3. Set up Terraform configurations for deploying the Lambda
4. Include necessary tests and documentation

## Project Structure Guidelines

Your implementation should follow our established monorepo structure:

```
├── modules/
│   └── transcribe-module/
│       ├── specs/           # Add specifications/design docs here
│       ├── src/             # Lambda function code goes here
│       │   ├── handlers/    # Lambda entry points
│       │   ├── services/    # Business logic
│       │   ├── models/      # Data structures
│       │   └── utils/       # Helper functions
│       └── tests/           # Unit/integration tests
├── libs/
│   └── base/                # Shared libraries to use if needed
├── infra/
│   ├── modules/
│   │   └── s3/              # s3 module was created here
│   │   └── lambda/          # Create Lambda Terraform module here
│   └── environments/
│       ├── dev/             # Dev environment configuration
│       └── prod/            # Production environment configuration
└── samples/
│   └── sample.mp3           # Use for testing
└── requirements.txt        # Include all shared dependencies here for the project
```

## Python Lambda Best Practices

1. Keep handler functions thin by delegating to service modules
2. Implement proper error handling and logging for aws
3. Use environment variables for configuration
4. Optimize package size by only including necessary dependencies
5. Create a requirements.txt file for dependencies. This should be stored at the root of the proejct and be shared by all modules in the system.
6. Implement basic unit tests for all components and store them in tests

## Terraform Implementation

Follow our terraform standards:
1. Create module resources in `infra/modules/lambda/`
2. Use snake_case for all resource names
3. Include appropriate variables, outputs, and documentation
4. Follow security best practices (IAM roles with least privilege, encryption)
5. Configure environment-specific settings in the environments directory

## Deliverables

1. Complete Lambda function code with proper modularization
2. Terraform module for Lambda deployment
3. Environment-specific Terraform configurations
4. Unit tests for the Lambda function
5. Documentation for usage and configuration

Please ensure all code is properly formatted, validated, and follows our established naming conventions and standards.