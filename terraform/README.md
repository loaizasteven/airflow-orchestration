# Terraform Configuration for Airflow Project

This directory contains Terraform configuration files for provisioning AWS infrastructure to support the Airflow project.

## Overview

This Terraform configuration creates basic AWS infrastructure including:
- An S3 bucket with a randomly generated name for data storage
- Proper bucket ownership controls and access control lists (ACL)
- Default resource tagging for organization and cost tracking

## Prerequisites

Before using this Terraform configuration, ensure you have:

1. **Terraform installed** (version ~> 1.2)
   ```bash
   # Install via Homebrew (macOS)
   brew install terraform
   
   # Or download from https://terraform.io/downloads
   ```

2. **AWS CLI configured** with appropriate credentials
   ```bash
   aws configure
   ```

3. **AWS IAM permissions** for the following services:
   - S3 (bucket creation, ownership controls, ACL management)
   - IAM (user creation, policy attachments, access key management) - required for `set_aws_iam/` configuration
   - Random provider (for bucket name generation)

## Configuration

### Variables

The configuration uses the following variables:

- `aws_region` (string): AWS region where resources will be created
  - Default: `us-east-1`
  - Description: AWS region for all resources

### Default Tags

All resources are automatically tagged with:
- `Project`: airflow
- `Environment`: development
- `Owner`: SLoaiza
- `Repository`: airflow

## Usage

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Plan the deployment

```bash
terraform plan
```

### Apply the configuration

```bash
terraform apply
```

### Destroy the infrastructure (when no longer needed)

```bash
terraform destroy
```

### Custom AWS Region

To deploy to a different AWS region:

```bash
terraform apply -var="aws_region=us-west-2"
```

## IAM User and Access Key Management

### Creating IAM User with Access Keys

The `set_aws_iam/` directory contains Terraform configuration for creating an IAM user with programmatic access keys. This is essential for applications that need to interact with AWS services programmatically.

#### Deploy IAM User

```bash
# Navigate to the IAM configuration directory
cd terraform/set_aws_iam

# Initialize Terraform
terraform init

# Plan the IAM user deployment
terraform plan

# Apply the configuration
terraform apply
```

#### Retrieve Access Keys Programmatically

After applying the IAM configuration, you can retrieve the access keys in several ways:

**Method 1: Using Terraform Output**
```bash
# Get the Access Key ID (safe to display)
terraform output access_key_id

# Get the Secret Access Key (sensitive)
terraform output -raw secret_access_key
```

**Method 2: Using Terraform Output in JSON Format**
```bash
# Get all outputs in JSON format
terraform output -json

# Parse specific values using jq
terraform output -json | jq -r '.access_key_id.value'
terraform output -json | jq -r '.secret_access_key.value'
```

**Method 3: Save to Environment Variables**
```bash
# Export to environment variables for immediate use
export AWS_ACCESS_KEY_ID=$(terraform output -raw access_key_id)
export AWS_SECRET_ACCESS_KEY=$(terraform output -raw secret_access_key)
```

**Method 4: Save to AWS Credentials File**
```bash
# Create AWS credentials file entry
echo "[airflow-user]" >> ~/.aws/credentials
echo "aws_access_key_id = $(terraform output -raw access_key_id)" >> ~/.aws/credentials
echo "aws_secret_access_key = $(terraform output -raw secret_access_key)" >> ~/.aws/credentials
```

**Method 5: Using in Scripts**
```bash
#!/bin/bash
# Example script to retrieve and use access keys

ACCESS_KEY_ID=$(cd terraform/set_aws_iam && terraform output -raw access_key_id)
SECRET_ACCESS_KEY=$(cd terraform/set_aws_iam && terraform output -raw secret_access_key)

# Use the credentials with AWS CLI
aws configure set aws_access_key_id $ACCESS_KEY_ID --profile airflow-user
aws configure set aws_secret_access_key $SECRET_ACCESS_KEY --profile airflow-user
aws configure set region us-east-1 --profile airflow-user

# Test the configuration
aws s3 ls --profile airflow-user
```

### Security Best Practices

⚠️ **Important Security Considerations:**

1. **Never commit access keys to version control**
2. **Use environment variables or AWS credentials file for local development**
3. **Rotate access keys regularly**
4. **Use IAM roles instead of access keys when possible (e.g., EC2 instances, Lambda functions)**
5. **Apply principle of least privilege - grant only necessary permissions**

### IAM User Permissions

The created IAM user has the following permissions:
- **IAM Full Access**: Can manage IAM resources
- **S3 Full Access**: Can manage S3 buckets and objects

> **Note**: These are broad permissions suitable for development. For production, consider creating custom policies with minimal required permissions.

### Rotating Access Keys

To rotate the access keys:

```bash
# Navigate to IAM configuration directory
cd terraform/set_aws_iam

# Taint the access key resource to force recreation
terraform taint aws_iam_access_key.terraform_user_key

# Apply to create new access keys
terraform apply

# Update your applications with the new keys
# Then remove the old keys from AWS console if needed
```

### Programmatic Access in Applications

**Python Example (using boto3):**
```python
import boto3
import subprocess
import json

# Get credentials from Terraform output
def get_terraform_credentials():
    result = subprocess.run(['terraform', 'output', '-json'], 
                          cwd='terraform/set_aws_iam', 
                          capture_output=True, text=True)
    outputs = json.loads(result.stdout)
    
    return {
        'access_key_id': outputs['access_key_id']['value'],
        'secret_access_key': outputs['secret_access_key']['value']
    }

# Use the credentials
creds = get_terraform_credentials()
s3_client = boto3.client('s3',
                        aws_access_key_id=creds['access_key_id'],
                        aws_secret_access_key=creds['secret_access_key'],
                        region_name='us-east-1')

# List S3 buckets
response = s3_client.list_buckets()
print(response['Buckets'])
```

**Node.js Example:**
```javascript
const AWS = require('aws-sdk');
const { execSync } = require('child_process');

// Get credentials from Terraform output
function getTerraformCredentials() {
    const output = execSync('terraform output -json', { 
        cwd: 'terraform/set_aws_iam' 
    });
    const outputs = JSON.parse(output.toString());
    
    return {
        accessKeyId: outputs.access_key_id.value,
        secretAccessKey: outputs.secret_access_key.value
    };
}

// Configure AWS SDK
const credentials = getTerraformCredentials();
AWS.config.update({
    accessKeyId: credentials.accessKeyId,
    secretAccessKey: credentials.secretAccessKey,
    region: 'us-east-1'
});

// Use AWS services
const s3 = new AWS.S3();
s3.listBuckets((err, data) => {
    if (err) console.log(err, err.stack);
    else console.log(data.Buckets);
});
```

## Resources Created

### Main Infrastructure
| Resource Type | Name/Description |
|---------------|------------------|
| `aws_s3_bucket` | S3 bucket with randomly generated name (prefix: `airflow_dev`) |
| `aws_s3_bucket_ownership_controls` | Bucket ownership controls set to "BucketOwnerPreferred" |
| `aws_s3_bucket_acl` | Bucket ACL set to "private" |
| `random_pet` | Random name generator for S3 bucket |

### IAM Resources (in `set_aws_iam/` directory)
| Resource Type | Name/Description |
|---------------|------------------|
| `aws_iam_user` | IAM user named "aws-airflow" for programmatic access |
| `aws_iam_user_policy_attachment` | IAM Full Access policy attachment |
| `aws_iam_user_policy_attachment` | S3 Full Access policy attachment |
| `aws_iam_access_key` | Access key pair for the IAM user |

## State Management

This configuration uses a **local backend** for state management. The Terraform state file (`terraform.tfstate`) will be stored locally in this directory.

> **Note**: For production environments, consider using a remote backend (e.g., S3 with DynamoDB for state locking) for better collaboration and state management.

## Provider Versions

- **AWS Provider**: ~> 5.38.0
- **Random Provider**: ~> 3.6.0

## Security Considerations

### S3 Security
- The S3 bucket is configured with private ACL by default
- Bucket ownership controls are set to "BucketOwnerPreferred"
- All resources are tagged for proper identification and cost tracking

### IAM Security
- IAM user access keys are marked as sensitive in Terraform outputs
- Access keys should never be committed to version control
- Consider using IAM roles instead of access keys for production workloads
- Regularly rotate access keys for security best practices
- The IAM user currently has broad permissions (IAM Full Access + S3 Full Access) - consider restricting for production use

## Troubleshooting

### Common Issues

1. **AWS credentials not configured**: Ensure AWS CLI is properly configured with `aws configure`
2. **Insufficient permissions**: Verify your AWS user/role has necessary S3 permissions
3. **Region-specific issues**: Some AWS services may not be available in all regions

### Getting Help

- Check the Terraform documentation: https://terraform.io/docs
- AWS Provider documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs 