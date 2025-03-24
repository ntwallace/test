variable "app" { type = string }
variable "service" { type = string }
variable "context" { type = string }
variable "dockerfile" {
  type    = string
  default = "Dockerfile"
}
