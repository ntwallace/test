data "aws_redshift_cluster" "this" {
  cluster_identifier = var.redshift_cluster_identifier
}

locals {
  app                  = var.app
  name                 = "${var.app}-zero-etl"
  rds_cluster_arn      = var.rds_cluster_arn
  redshift_cluster_arn = data.aws_redshift_cluster.this.arn
  tags = {
    app         = local.app
    provisioner = "terraform"
  }
}

