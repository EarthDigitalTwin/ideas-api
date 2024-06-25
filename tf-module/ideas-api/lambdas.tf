resource "aws_lambda_function" "ideas_api" {
  filename      = local.lambda_file_name
  source_code_hash = filebase64sha256(local.lambda_file_name)
  function_name = "${var.prefix}-ideas_api"
  role          = var.lambda_processing_role_arn
  handler       = "ideas_api.web_service.handler"
  runtime       = "python3.9"
  timeout       = 300
  environment {
    variables = {
      LOG_LEVEL = var.log_level
      aws_region = var.aws_region
      ES_URL = data.aws_elasticsearch_domain.ideas-es.endpoint
      ES_PORT = 443
      SNS_TOPIC = aws_sns_topic.ideas_api_main_topic.arn
      ADMIN_GROUPS = var.admin_groups
    }
  }

  vpc_config {
    subnet_ids         = var.ideas_api_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}

resource "aws_lambda_function" "ideas_api_updater_trigger" {
  filename      = local.lambda_file_name
  function_name = "${var.prefix}-ideas_api_updater_trigger"
  source_code_hash = filebase64sha256(local.lambda_file_name)
  role          = var.lambda_processing_role_arn
  handler       = "ideas_api.job_update_lambda_entry.trigger_job_updater"
  runtime       = "python3.9"
  timeout       = 300
  environment {
    variables = {
      LOG_LEVEL = var.log_level
//      COLLECTION_CREATION_LAMBDA_NAME = aws_lambda_function.ideas_api.arn
      ES_URL = data.aws_elasticsearch_domain.ideas-es.endpoint
      ES_PORT = 443
      SNS_TOPIC = aws_sns_topic.ideas_api_main_topic.arn
    }
  }

  vpc_config {
    subnet_ids         = var.ideas_api_lambda_subnet_ids
    security_group_ids = local.security_group_ids_set ? var.security_group_ids : [aws_security_group.unity_cumulus_lambda_sg[0].id]
  }
  tags = var.tags
}
