locals {
  environment             = "live"
  app_name                = "live-powerx-api"
  upstream_basis          = "live-basis"
  upstream_data_pipelines = "live-data-pipelines"
  app                     = terraform.workspace == "default" ? local.app_name : "${local.app_name}-${terraform.workspace}"

  dashboard_web_domain = "dashboard.powerx.co"
  powerx_api_domain    = "api-v2.${local.environment}.powerx.co"
  logo_s3_bucket_name  = "live-dashboard-media"

  vpc_id                      = data.aws_vpc.this.id
  public_subnet_ids           = data.aws_subnets.public.ids
  private_subnet_ids          = data.aws_subnets.private.ids
  private_subnets_cidr_blocks = [for s in data.aws_subnet.private_subnets : s.cidr_block]

  ssm__dp_domain           = data.aws_ssm_parameter.dp_domain.name
  ssm__dp_api_key          = data.aws_ssm_parameter.dp_api_key.name
  ssm__redis_host          = data.aws_ssm_parameter.redis_host.name
  ssm__redis_port          = data.aws_ssm_parameter.redis_port.name
  ssm__sendgrid_api_key    = data.aws_ssm_parameter.sendgrid_api_key.name
  ssm__media_endpoint      = data.aws_ssm_parameter.media_endpoint.name
  ssm__media_public_key_id = data.aws_ssm_parameter.media_public_key_id.name
  ssm__media_private_key   = data.aws_ssm_parameter.media_private_key.name
}

data "aws_vpc" "this" {
  filter {
    name   = "tag:app"
    values = [local.upstream_basis]
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "tag:Name"
    values = ["*-public-*"]
  }
  filter {
    name   = "tag:app"
    values = [local.upstream_basis]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Name"
    values = ["*-private-*", "*-infra-*"]
  }
  filter {
    name   = "tag:app"
    values = [local.upstream_basis]
  }
}

data "aws_subnet" "private_subnets" {
  count = length(local.private_subnet_ids)
  id    = local.private_subnet_ids[count.index]
}

data "aws_ssm_parameter" "redis_host" {
  name = "/${local.upstream_basis}-redis/host"
}
data "aws_ssm_parameter" "redis_port" {
  name = "/${local.upstream_basis}-redis/port"
}


data "aws_ssm_parameter" "dp_domain" {
  name = "/${local.upstream_basis}-data-pipeline/api/domain"
}
data "aws_ssm_parameter" "dp_api_key" {
  name = "/${local.upstream_basis}-data-pipeline/api/apikey"
}
data "aws_ssm_parameter" "sendgrid_api_key" {
  name = "/external/sendgrid/api_key"
}
data "aws_ssm_parameter" "media_endpoint" {
  name = "/${local.environment}-dashboard-media/endpoint"
}
data "aws_ssm_parameter" "media_public_key_id" {
  name = "/${local.environment}-dashboard-media/public-key-id"
}
data "aws_ssm_parameter" "media_private_key" {
  name = "/${local.environment}-dashboard-media/private-key"
}

data "aws_ssm_parameter" "timestream_database_name_hvac_data" {
  name = "/timestream/${local.upstream_data_pipelines}-hvac-data/name"
}
data "aws_ssm_parameter" "timestream_table_arn_control_zones" {
  name = "/timestream/${local.upstream_data_pipelines}-hvac-data/control-zones/arn"
}
data "aws_ssm_parameter" "timestream_table_name_control_zones" {
  name = "/timestream/${local.upstream_data_pipelines}-hvac-data/control-zones/name"
}
data "aws_ssm_parameter" "timestream_database_name_temperature_data" {
  name = "/timestream/${local.upstream_data_pipelines}-temperature-data/name"
}
data "aws_ssm_parameter" "timestream_table_arn_temperature_places" {
  name = "/timestream/${local.upstream_data_pipelines}-temperature-data/temperature-places/arn"
}
data "aws_ssm_parameter" "timestream_table_name_temperature_places" {
  name = "/timestream/${local.upstream_data_pipelines}-temperature-data/temperature-places/name"
}
data "aws_ssm_parameter" "timestream_database_name_electricity_data" {
  name = "/timestream/${local.upstream_data_pipelines}-electricity-data/name"
}
data "aws_ssm_parameter" "timestream_table_arn_circuits" {
  name = "/timestream/${local.upstream_data_pipelines}-electricity-data/circuits/arn"
}
data "aws_ssm_parameter" "timestream_table_name_circuits" {
  name = "/timestream/${local.upstream_data_pipelines}-electricity-data/circuits/name"
}
data "aws_ssm_parameter" "timestream_table_arn_pes_averages" {
  name = "/timestream/${local.upstream_data_pipelines}-electricity-data/pes-averages/arn"
}
data "aws_ssm_parameter" "timestream_table_name_pes_averages" {
  name = "/timestream/${local.upstream_data_pipelines}-electricity-data/pes-averages/name"
}
