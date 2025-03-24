output "name" {
  value      = "${aws_ecr_repository.this.repository_url}:${local.commit_sha}"
  depends_on = [null_resource.ecr_image]
}
