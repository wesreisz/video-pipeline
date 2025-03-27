I need to update my AWS Lambda code (written in Python) for my video processing pipeline. My pipeline processes videos that are uploaded to S3, and I want to attach custom metadata to each video. The metadata should include:

- speaker: a comma-separated list of speaker names (which I want to split into an array)
- title: the title of the talk
- track: the track of the talk (e.g., "Data Science")
- day: the day of the event (in YYYY-MM-DD format)

I want to:

1. **Upload a video to S3 with metadata.**  
   Provide a sample AWS CLI command that uploads a file (e.g., "my_video.mp4") to S3 and includes the metadata mentioned above.

2. **In my Lambda function, retrieve the metadata from the S3 object.**  
   Use Boto3's `head_object` to get the metadata from the uploaded S3 file. Parse the metadata so that:
   - The "speaker" field is split into an array (list of names).
   - The other fields ("title", "track", and "day") are extracted as strings.

3. **Upsert the resulting data to Pinecone.**  
   After generating an embedding vector for the content (you can use a dummy vector for now), upsert this vector into a Pinecone index. Use the S3 object's key as the vector ID, and include the extracted metadata as part of the Pinecone metadata payload.

Please generate the complete code including:
- A sample AWS CLI command for the S3 upload.
- A complete Python code snippet for the Lambda function that:
  - Extracts the bucket and key from the event,
  - Retrieves the object's metadata,
  - Processes the metadata (splitting the speaker string into a list),
  - Generates a dummy embedding vector,
  - Initializes the Pinecone index, and
  - Upserts the vector with the metadata into Pinecone.

Include clear comments in the code explaining each section.

## References
- [OpenAI Python Client](https://github.com/openai/openai-python)