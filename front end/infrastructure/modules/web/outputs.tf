output "dns" {
  value = "${local.domain} CNAME ${aws_cloudfront_distribution.this.domain_name}"
}
