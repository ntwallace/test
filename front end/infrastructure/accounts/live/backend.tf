terraform {
  backend "s3" {
    role_arn = "arn:aws:iam::510548384854:role/terraform/TerraformStateFileAccess"
    bucket   = "powerx-infrastructure"
    region   = "us-east-2"
    key      = "live--us-east-1--dashboard-web.tfstate"
  }
}
