provider "aws" {
    region = var.aws_region

    default_tags {
        tags = {
        Project     = "airflow"
        Environment = "development"
        Owner       = "SLoaiza"
        Repository  = "airflow"
        }
    }
}

// Create a random name for S3 bucket
resource "random_pet" "lambda_bucket_name"{
    prefix = "airflow_dev"
    length = 4
}

// Create an S3 bucket
resource "aws_s3_bucket" "lambda_bucket" {
    bucket = random_pet.lambda_bucket_name.id
}

// Enable versioning for the S3 bucket
resource "aws_s3_bucket_ownership_controls" "lambda_bucket" {
  bucket = aws_s3_bucket.lambda_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

// Set the ownership controls for the S3 bucket
resource "aws_s3_bucket_acl" "lambda_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.lambda_bucket]

  bucket = aws_s3_bucket.lambda_bucket.id
  // The canned_acl is used to set the access control list for the bucket
  // privaete means that only the bucket owner has access to the objects in the bucket
  acl    = "private"
}