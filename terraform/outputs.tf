output "apprunner_service_url" {
  description = "The public HTTPS URL of the deployed AWS App Runner service"
  value       = "https://${aws_apprunner_service.clinic_service.service_url}"
}

output "ecr_repository_url" {
  description = "Amazon ECR Docker repository URL"
  value       = aws_ecr_repository.clinic_ecr.repository_url
}

output "apprunner_role_arn" {
  description = "IAM Role ARN created for App Runner ECR access"
  value       = aws_iam_role.apprunner_ecr_role.arn
}
