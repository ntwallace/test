resource "null_resource" "ecr_image" {
  triggers = {
    source_path_sha = local.source_path_sha
    commit_sha      = local.commit_sha
  }
  provisioner "local-exec" {
    working_dir = local.source_path
    environment = {
      REPOSITORY = aws_ecr_repository.this.repository_url
      USERNAME   = nonsensitive(data.aws_ecr_authorization_token.this.user_name)
      PASSWORD   = nonsensitive(data.aws_ecr_authorization_token.this.password)
      TAG        = local.commit_sha
      DOCKERFILE = local.dockerfile
    }
    command = <<EOF
#!/bin/bash
#!/usr/bin/env sh
set -ex

echo $PASSWORD | docker login $REPOSITORY --username $USERNAME --password-stdin

IMAGE="$REPOSITORY:$TAG"
docker buildx build --provenance=false --push --platform linux/arm64 \
  --cache-from type=local,src=$(pwd)/.docker-buildx-cache \
  --cache-to type=local,dest=$(pwd)/.docker-buildx-cache-latest,mode=max \
  --tag $IMAGE --file $DOCKERFILE .

# replace cache: https://docs.docker.com/build/ci/github-actions/cache/#local-cache
rm -rf $(pwd)/.docker-buildx-cache
mv -v  $(pwd)/.docker-buildx-cache-latest $(pwd)/.docker-buildx-cache

EOF
  }
  depends_on = [aws_ecr_repository.this]
}
resource "aws_ecr_repository" "this" {
  force_delete         = true
  name                 = local.app
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
  tags = local.tags
}
resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.id
  policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 10 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 10
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })
}
