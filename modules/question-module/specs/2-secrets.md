This project uses a secret manager on aws to store secrets. Add access-list-location to the secrets and store this value in it: https://dev-access-list.s3.us-east-1.amazonaws.com/access.csv

Then set that value as a global varible in the function.