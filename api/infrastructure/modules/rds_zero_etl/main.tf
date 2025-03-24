resource "aws_rds_integration" "this" {
  integration_name = local.name
  source_arn       = local.rds_cluster_arn
  target_arn       = local.redshift_cluster_arn

  lifecycle {
    ignore_changes = [
      kms_key_id
    ]
  }

  tags = local.tags
}