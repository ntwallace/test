terraform {
  required_version = "<2.0.0, >1.4.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.64.0"
    }
  }
}
