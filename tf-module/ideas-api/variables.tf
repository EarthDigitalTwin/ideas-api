variable "log_level" {
  type = string
  default = "20"
  description = "Lambda Log Level. Follow Python3 log level numbers info=20, warning=30, etc..."
}

variable "prefix" {
  type = string
}
variable "aws_region" {
  type    = string
  default = "us-west-2"
}
variable "ideas_api_lambda_subnet_ids" {
  description = "Subnet IDs for Lambdas"
  type        = list(string)
  default     = null
}
variable "ideas_api_lambda_vpc_id" {
  type = string
}

variable "security_group_ids" {
  description = "Security Group IDs for Lambdas"
  type        = list(string)
  default     = null
}

variable "tags" {
  description = "Tags to be applied to Cumulus resources that support tags"
  type        = map(string)
  default     = {}
}

variable "ideas_es_cluster_instance_count" {
  type = number
  default = 2
  description = "How many EC2 instances for Opensearch"
}

variable "ideas_es_cluster_instance_type" {
  type = string
  default = "r5.large.elasticsearch"
  description = "EC2 instance type for Opensearch"
}

variable "lambda_processing_role_arn" {
  type = string
}

variable "job_lis_lambda_arn" {
  type = string
  description = "ARN for LIS entry Lambda"
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_client_id_list" {
  type = string
}

variable "admin_groups" {
  type = string
  description = "JSON array of admin groups example: [\"group1\", \"group2\"]"
}