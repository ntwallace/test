provider "aws" {
  region = "us-east-1"
}
locals {
  app    = var.app
  domain = var.domain
}
module "web" {
  source = "../../modules/web"
  app    = local.app
  domain = local.domain
}
