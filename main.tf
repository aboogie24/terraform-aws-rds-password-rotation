# Create cloudwatch event bridge

data "aws_partition" "current" {} 
data "aws_region" "curent" {} 
data "aws_caller_identity" "current" {} 

locals { 
  full_name = "${var.name}-${var.environment}-master-rotation"
}

resource "aws_cloudwatch_event_rule" "password-lambda-rotation" {
  name                = var.cloudwatch_rule_name
  description         = "Password Lambda Rotation"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "password-lambda-rotation" {
  arn  = aws_lambda_function.function.arn
  rule = aws_cloudwatch_event_rule.password-lambda-rotation.name
}


resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.password-lambda-rotation.arn
}

resource "aws_cloudwatch_log_group" "main" {
  name = "/aws/lambda/${var.lambda_function}"
  retention_in_days = var.cloudwatch_logs_retention_days

  tags = { 
    Name = "Name"
  }
}

resource "aws_cloudwatch_log_stream" "Log_stream" {
  name = var.lambda_function
  log_group_name = aws_cloudwatch_log_group.main.name
}


data "aws_iam_policy_document" "assume_role" {
  statement { 
    effect = "Allow"
    actions = ["sts:AssumeRole"]

    principals { 
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "main" {
  statement { 
    effect = "Allow"

    actions = [ 
      "logs:CreateLogStream", 
      "logs:CreateLogGroup",
      "logs:PutLogEvents",
    ]

    resources = ["arn:${data.aws_partition.current.partition}:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.lambda_function}:log-stream:${var.lambda_function}",
                 "arn:${data.aws_partition.current.partition}:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.lambda_function}:log-stream:*",
    ]
    
  }
  statement {
    effect = "Allow"

    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:PutParameter"
    ]

    resources = ["arn:${data.aws_partition.current.partition}:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/${var.ssm_parameter_value}"]
  }

  statement {
    effect = "Allow"

    actions = [
      "rds:ModifyDBInstance",
    ] 

    resources = ["arn:${data.aws_partition.current.partition}:rds:${var.region}:${data.aws_caller_identity.current.account_id}:db:${var.db_name}"] 
  }
  
}

resource "aws_iam_role" "main" {
  name = "lambda-${local.full_name}-Role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy" "main" {
  name = "lamdba-${local.full_name}-Policy"
  role = aws_iam_role.main.id 
  policy = data.aws_iam_policy_document.main.json
}

data "archive_file" "lambda" { 
  type = "zip"
  source_dir = "${path.module}/lambda_function"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "function" {
  function_name = var.lambda_function
  runtime       = "python3.8"
  role          = aws_iam_role.main.arn 
  handler = "lambda_function.lambda_handler"
  memory_size = 128 
  timeout = 60 
  filename = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  tags = var.tags

  environment {
    variables = {
      "SSM_PARAMETER" = "/${var.ssm_parameter_value}",
      "DB_NAME" = "${var.db_name}", 
      "REGION" = var.region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.main,
  ]
  



}
