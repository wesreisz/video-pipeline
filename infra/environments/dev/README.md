## Delete the Infra
To destroy the infra, run terraform destroy. The secret store will not automatically
delete for a few days (for safety). This command forces the deletion:
`aws secretsmanager delete-secret --secret-id dev-video-pipeline-secrets --force-delete-without-recovery`
