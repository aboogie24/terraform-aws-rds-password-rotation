

module "Password-Rotation" {
  source                         = "../../"
  name                           = "Master-Password"
  region                         = "us-west-1"
  environment                    = "dev"
  schedule_expression            = "rate(5 minutes)"
  cloudwatch_logs_retention_days = "14"
  s3_bucket                      = "lambdabuckettestdsd"
  s3_key                         = "master_password_rotation/master_password_rotation.zip"
  ssm_parameter_value            = "test/db/password"
  db_name                        = "test-db"
  slack_url = "https://hooks.slack.com/services/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"
}
