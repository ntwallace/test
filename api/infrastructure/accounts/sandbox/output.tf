output "powerx_api_dns" {
  value = "DNS: ${module.powerx_api.api_domain} CNAME ${module.powerx_api.lb_dns}"
}
