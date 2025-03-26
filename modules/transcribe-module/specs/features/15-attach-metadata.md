When the file is uploaded to s3, in most cases we will attach metadata to the file. The metadata will include:
- speaker (this is the speaker in the talk it could be empty or multiple speakers)
- title (this is the actual title of the talk)
- track (this is the track the talk was in)
- day (this is the day of teh week the talk was on... ie: monday)

If this information is available to the file uploaded to s3, I want to update the transcribe_handler.py to pull it from the file and embed in the event bridge response
for the next step in the pipeline.

If the information is not available, I do not want it to fail but to continue with the rest of the pipeline.