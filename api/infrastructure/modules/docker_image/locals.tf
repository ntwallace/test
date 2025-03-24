locals {
  app     = var.app
  service = var.service
  name    = "${local.app}-${local.service}"
  
  source_path  = var.context
  dockerfile   = var.dockerfile
  path_include = ["pyproject.toml", "alembic.ini", "**/alembic/**","**/app/**"]
  path_exclude = ["**/__pycache__/**"]
  files = sort(setsubtract(
    setunion([for f in local.path_include : fileset(local.source_path, f)]...),
    setunion([for f in local.path_exclude : fileset(local.source_path, f)]...),
  ))
  source_path_sha = sha1(join("", [for f in local.files : filesha1("${local.source_path}/${f}")]))
  commit_sha      = data.external.git.result.version
  tags = {
    app         = local.app
    service     = local.service
    provisioner = "terraform"
  } 
}
data "external" "git" {
  program = ["sh", "-c", <<-EOF
    set -e
    version=$(git describe --always HEAD 2>>/dev/null || git rev-parse --short HEAD)
    echo '{"version": "'$version'"}'
    EOF
  ]
}
data "aws_ecr_authorization_token" "this" {}
data "aws_caller_identity" "this" {}
data "aws_region" "this" {}