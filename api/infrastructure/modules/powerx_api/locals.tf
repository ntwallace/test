locals {
  app     = var.app
  service = "api"
  name    = "${local.app}-${local.service}"

  aws_region                 = data.aws_region.this.name
  vpc_id                     = var.vpc_id
  public_subnet_ids          = var.alb_subnet_ids
  private_subnet_ids         = var.ecs_service_subnet_ids
  ecs_service_subnet_ids     = var.ecs_service_subnet_ids
  private_subnet_cidr_blocks = var.private_subnets_cidr_blocks

  powerx_database_name = "powerx"

  api_domain           = var.api_domain
  dashboard_web_domain = var.dashboard_web_domain
  logo_s3_bucket_name  = var.logo_s3_bucket_name

  timestream_database_name_hvac_data  = var.timestream_database_name_hvac_data
  timestream_table_name_control_zones = var.timestream_table_name_control_zones
  timestream_table_arn_control_zones  = var.timestream_table_arn_control_zones

  timestream_database_name_temperature_data = var.timestream_database_name_temperature_data
  timestream_table_name_temperature_places  = var.timestream_table_name_temperature_places
  timestream_table_arn_temperature_places   = var.timestream_table_arn_temperature_places

  timestream_database_name_electricity_data = var.timestream_database_name_electricity_data
  timestream_table_name_circuits            = var.timestream_table_name_circuits
  timestream_table_arn_circuits             = var.timestream_table_arn_circuits
  timestream_table_name_pes_averages        = var.timestream_table_name_pes_averages
  timestream_table_arn_pes_averages         = var.timestream_table_arn_pes_averages

  tags = {
    app         = local.app
    service     = local.service
    provisioner = "terraform"
  }
}

data "aws_region" "this" {}


