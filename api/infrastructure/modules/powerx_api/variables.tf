variable "app" {
  type = string
}
variable "vpc_id" {
  type = string
}
variable "alb_subnet_ids" {
  type = list(string)
}
variable "ecs_service_subnet_ids" {
  type = list(string)
}
variable "private_subnets_cidr_blocks" {
  type = list(string)
}
variable "api_domain" {
  type = string
}
variable "logo_s3_bucket_name" {
  type = string
}
variable "dashboard_web_domain" {
  type = string
}

# Timestream databases/tables
variable "timestream_database_name_hvac_data" { type = string }
variable "timestream_table_name_control_zones" { type = string }
variable "timestream_table_arn_control_zones" { type = string }

variable "timestream_database_name_temperature_data" { type = string }
variable "timestream_table_name_temperature_places" { type = string }
variable "timestream_table_arn_temperature_places" { type = string }

variable "timestream_database_name_electricity_data" { type = string }
variable "timestream_table_name_circuits" { type = string }
variable "timestream_table_arn_circuits" { type = string }
variable "timestream_table_name_pes_averages" { type = string }
variable "timestream_table_arn_pes_averages" { type = string }

# SSM
variable "ssm__media_endpoint" { type = string }
variable "ssm__media_public_key_id" { type = string }
variable "ssm__media_private_key" { type = string }
variable "ssm__dp_domain" { type = string }
variable "ssm__dp_api_key" { type = string }
variable "ssm__redis_host" { type = string }
variable "ssm__redis_port" { type = string }
variable "ssm__sendgrid_api_key" { type = string }
