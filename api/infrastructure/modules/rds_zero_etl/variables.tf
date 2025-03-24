variable "app" {
  type = string
}
variable "rds_cluster_arn" {
  description = "The RDS cluster ARN"
  type = string
}
variable "redshift_cluster_identifier" {
  description = "The Redshift cluster identifier"
  type = string
}