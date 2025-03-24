output "lb_dns" {
  value = aws_lb.this.dns_name
}
output "api_domain" {
  value = local.api_domain
}
output "rds_cluster_arn" {
  value = module.cluster.cluster_arn
}