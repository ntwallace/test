terraform {
  backend "s3" {
    bucket   = "powerx-infrastructure"
    key      = "live--us-east-2--powerx-api-v2.tfstate"
    region   = "us-east-2"
    assume_role = {
      role_arn = "arn:aws:iam::510548384854:role/terraform/TerraformStateFileAccess"
    }
  }
}
