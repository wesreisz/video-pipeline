#!/bin/bash

# Check if PINECONE_API_KEY is set
if [ -z "$PINECONE_API_KEY" ]; then
    echo "Error: PINECONE_API_KEY environment variable is not set"
    exit 1
fi

HOST="https://talk-embeddings-ik1lw1x.svc.aped-4627-b74a.pinecone.io"
curl -X POST "$HOST/vectors/delete" \
  -H "Content-Type: application/json" \
  -H "Api-Key: $PINECONE_API_KEY" \
  -d '{"delete_all": true}'
