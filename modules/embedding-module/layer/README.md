# Embedding Module Lambda Layer

This Lambda layer provides the required dependencies for the embedding module's Lambda function.

## Dependencies

The layer includes:
- OpenAI Python Client (>=1.0.0)
- Pinecone Client (>=2.2.0)
- Python JSON Logger (>=2.0.0)
- Typing Extensions (>=4.5.0)

## Building the Layer

1. Install dependencies:
```bash
./1-install.sh
```

2. Package the layer:
```bash
./2-package.sh
```

The packaged layer will be available as `layer_content.zip`.

## Layer Structure

The layer follows AWS Lambda's Python layer structure:
```
python/
└── lib/
    └── python3.13/
        └── site-packages/
            ├── openai/
            ├── pinecone/
            └── ...
```

## Usage

1. Deploy the layer to AWS Lambda
2. Attach the layer to the embedding module Lambda function
3. Configure the following environment variables in the Lambda function:
   - `OPENAI_API_KEY`: Required for OpenAI API access
   - `OPENAI_TIMEOUT`: Optional, default 20.0 seconds
   - `OPENAI_MAX_RETRIES`: Optional, default 3 retries
   - `OPENAI_BASE_URL`: Optional, custom API endpoint
   - `OPENAI_ORG_ID`: Optional, organization ID 