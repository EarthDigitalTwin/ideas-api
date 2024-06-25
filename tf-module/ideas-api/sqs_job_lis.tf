resource "aws_sqs_queue" "ideas_jobs_lis_queue" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue
  name                      = "${var.prefix}-ideas_jobs_lis_queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  visibility_timeout_seconds = 310
  receive_wait_time_seconds = 0
  policy = templatefile("${path.module}/sqs_policy.json", {
    region: var.aws_region,
    roleArn: var.lambda_processing_role_arn,
    accountId: local.account_id,
    sqsName: "${var.prefix}-ideas_jobs_lis_queue",
  })
//  redrive_policy = jsonencode({
//    deadLetterTargetArn = aws_sqs_queue.terraform_queue_deadletter.arn
//    maxReceiveCount     = 4
//  })
//  tags = {
//    Environment = "production"
//  }
}

resource "aws_sns_topic_subscription" "ideas_api_sns_lis_subscription" { // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription
  topic_arn = aws_sns_topic.ideas_api_main_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.ideas_jobs_lis_queue.arn
  filter_policy_scope = "MessageBody"  // MessageAttributes. not using attributes
  filter_policy = templatefile("${path.module}/ideas_api_job_lis_filter_policy.json", {})
}

resource "aws_lambda_event_source_mapping" "ideas_job_lis_lambda_trigger" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping#sqs
  event_source_arn = aws_sqs_queue.ideas_jobs_lis_queue.arn
  function_name    = var.job_lis_lambda_arn
  batch_size = 1
  enabled = true
}