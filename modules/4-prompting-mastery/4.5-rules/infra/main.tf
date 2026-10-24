terraform {
  required_version = "~> 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  backend "s3" {
    bucket         = "claude-rules-demo-tfstate"
    key            = "envs/dev/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "claude-rules-demo-tflock"
    encrypt        = true
  }
}

locals {
  project = "claude-rules-demo"
  env     = "dev"

  common_tags = {
    environment = local.env
    owner       = "platform"
    managed_by  = "terraform"
    cost_center = "rnd"
  }
}

resource "aws_s3_bucket" "user_uploads" {
  bucket = "${local.project}-${local.env}-uploads"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "user_uploads" {
  bucket = aws_s3_bucket.user_uploads.id

  versioning_configuration {
    status = "Enabled"
  }
}
