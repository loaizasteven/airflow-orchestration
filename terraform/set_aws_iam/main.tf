provider "aws" {
  region = "us-east-1"

}

resource "aws_iam_user" "terraform_user" {
    name = "aws-airflow"
}

resource "aws_iam_user_policy_attachment" "admin_access" {
    user       = aws_iam_user.terraform_user.name
    policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}

// Set the IAM User policy for S3 Access
resource "aws_iam_user_policy_attachment" "aws_terraform_s3_policy" {
  user       = aws_iam_user.terraform_user.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

// Create access key for the IAM user
resource "aws_iam_access_key" "terraform_user_key" {
  user = aws_iam_user.terraform_user.name
}

// Output the access key ID (safe to display)
output "access_key_id" {
  value = aws_iam_access_key.terraform_user_key.id
}

// Output the secret access key (sensitive, will be hidden in logs)
output "secret_access_key" {
  value     = aws_iam_access_key.terraform_user_key.secret
  sensitive = true
}
