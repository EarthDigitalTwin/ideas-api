resource "aws_sns_topic" "ideas_api_main_topic" {  // https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic.html
  name              = "${var.prefix}-ideas_api_main_topic"
  kms_master_key_id = "alias/aws/sns"
}
