When event bridge sends the file to the chunking module, it will also send the metadata that was attached to the file. The event will look like this:
```json
{
    'statusCode': 200,
    'detail': {
        'records': [{
            's3': {
                'bucket': {'name': output_bucket},
                'object': {'key': output_key}
            },
            'metadata': metadata
        }]
    },
    'body': json.dumps({
        'message': 'Transcription completed successfully',
        'bucket': bucket,
        'original_file': key,
        'transcription_file': output_key,
        'metadata': metadata
    })
}
```

Update the message we push to the sqs queue to include the metadata. Just before pushing the message to the queue

Update this logging line to show the metadata that was sent to the queue as well.
```python
logger.info(f"Sent segment to SQS: MessageId={response['MessageId']}, ChunkId={chunk_id}")
```