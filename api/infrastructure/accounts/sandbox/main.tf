provider "aws" {
  region = "us-east-2"
}

module "powerx_api" {
  source = "../../modules/powerx_api"

  app = local.app

  vpc_id                      = local.vpc_id
  alb_subnet_ids              = local.public_subnet_ids
  ecs_service_subnet_ids      = local.private_subnet_ids
  private_subnets_cidr_blocks = local.private_subnets_cidr_blocks

  api_domain           = local.powerx_api_domain
  dashboard_web_domain = local.dashboard_web_domain
  logo_s3_bucket_name  = local.logo_s3_bucket_name

  timestream_database_name_hvac_data        = nonsensitive(data.aws_ssm_parameter.timestream_database_name_hvac_data.value)
  timestream_table_name_control_zones       = nonsensitive(data.aws_ssm_parameter.timestream_table_name_control_zones.value)
  timestream_table_arn_control_zones        = nonsensitive(data.aws_ssm_parameter.timestream_table_arn_control_zones.value)
  timestream_database_name_temperature_data = nonsensitive(data.aws_ssm_parameter.timestream_database_name_temperature_data.value)
  timestream_table_name_temperature_places  = nonsensitive(data.aws_ssm_parameter.timestream_table_name_temperature_places.value)
  timestream_table_arn_temperature_places   = nonsensitive(data.aws_ssm_parameter.timestream_table_arn_temperature_places.value)
  timestream_database_name_electricity_data = nonsensitive(data.aws_ssm_parameter.timestream_database_name_electricity_data.value)
  timestream_table_name_circuits            = nonsensitive(data.aws_ssm_parameter.timestream_table_name_circuits.value)
  timestream_table_arn_circuits             = nonsensitive(data.aws_ssm_parameter.timestream_table_arn_circuits.value)
  timestream_table_name_pes_averages        = nonsensitive(data.aws_ssm_parameter.timestream_table_name_pes_averages.value)
  timestream_table_arn_pes_averages         = nonsensitive(data.aws_ssm_parameter.timestream_table_arn_pes_averages.value)

  ssm__dp_domain           = local.ssm__dp_domain
  ssm__dp_api_key          = local.ssm__dp_api_key
  ssm__redis_host          = local.ssm__redis_host
  ssm__redis_port          = local.ssm__redis_port
  ssm__sendgrid_api_key    = local.ssm__sendgrid_api_key
  ssm__media_endpoint      = local.ssm__media_endpoint
  ssm__media_public_key_id = local.ssm__media_public_key_id
  ssm__media_private_key   = local.ssm__media_private_key
}

# Note:
#   As of 10/25/24, the rds_zero_etl module cannot be used.
#   The module uses the `aws_rds_integration` resource, and currently it does not support data
#   filter, but this is required to for an Aurora PostgreSQL source.
#   There is a ticket to support this feature in github:
#   https://github.com/hashicorp/terraform-provider-aws/issues/39762
#   Until this is implemented, the integration must be set manually.
#
# module "rds_zero_etl" {
#   source                      = "../../modules/rds_zero_etl"
#   app                         = local.app
#   rds_cluster_arn             = module.powerx_api.rds_cluster_arn
#   redshift_cluster_identifier = "${local.upstream_basis}-redshift"
# }