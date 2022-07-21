variable "lambda_function" {
  description = "Name of lambda function being used"
  type        = string
  default     = "lambda-Password-Rotation"
}

variable "region" {
  description = "REGION"
  type = string
  default     = "us-west-1"
}

variable "name"{ 
  description = "Master Password Rotation"
  type = string
}

variable "environment" {
  description = "Deployed Environment"
  type = string
}

variable "s3_bucket" {  
    description = "S3 Bucket Holding the Lambda Function zip"
    type = string
}

variable "s3_key" {  
    description = "S3 Bucket Holding the Lambda Function zip"
    type = string
}

variable "tags" {
  description = "Lamdba-TAGS"
  type        = map(string)
  default = {
    APPLICATION = "Password-Rotation"
    MANAGED     = "Terraform"
  }
}

variable "schedule_expression" {
  description = "Time for "
  type        = string
  default     = "rate(59 days)"
}

variable "cloudwatch_rule_name" {
  description = "Name of cloudwatch Rule"
  type        = string
  default     = "Master_Password_Rotation"
}

variable "cloudwatch_logs_retention_days" {
  description = "Retention Days"
  type = string 
  default = "14"
}

variable "ssm_parameter_value" {
  description = "SSM Parameter Store value to be changed"
  type = string 
}

variable "db_name" {
  description = "Database Target Name"
  type = string
}

variable "slack_url" {
  description = "Webhood for slack endpoint"
  type = string
}
