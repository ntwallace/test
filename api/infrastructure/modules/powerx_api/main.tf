# Data - S3
data "aws_s3_bucket" "logo_bucket" {
  bucket = var.logo_s3_bucket_name
}

# Data - SSM
data "aws_ssm_parameter" "dp_domain" {
  name = var.ssm__dp_domain
}
data "aws_ssm_parameter" "dp_api_key" {
  name = var.ssm__dp_api_key
}
data "aws_ssm_parameter" "redis_host" {
  name = var.ssm__redis_host
}
data "aws_ssm_parameter" "redis_port" {
  name = var.ssm__redis_port
}
data "aws_ssm_parameter" "sendgrid_api_key" {
  name = var.ssm__sendgrid_api_key
}
data "aws_ssm_parameter" "media_endpoint" {
  name = var.ssm__media_endpoint
}
data "aws_ssm_parameter" "media_public_key_id" {
  name = var.ssm__media_public_key_id
}
data "aws_ssm_parameter" "media_private_key" {
  name = var.ssm__media_private_key
}

# Database
module "cluster" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "9.9.1"

  name           = "${local.app}-db"
  engine         = "aurora-postgresql"
  engine_version = "16.4"
  instance_class = "db.t4g.medium"
  instances = {
    1 = {}
  }
  master_username = "root"
  manage_master_user_password = true
  database_name = local.powerx_database_name

  vpc_id                 = local.vpc_id
  create_db_subnet_group = true
  db_subnet_group_name   = "${local.app}-db-subnet-group"
  subnets                = local.private_subnet_ids
  publicly_accessible    = false

  create_security_group = true
  security_group_rules = {
    vpc_ingress = {
      cidr_blocks = local.private_subnet_cidr_blocks
    }
  }

  create_db_cluster_parameter_group      = true
  db_cluster_parameter_group_name        = local.app
  db_cluster_parameter_group_family      = "aurora-postgresql16"
  db_cluster_parameter_group_description = "${local.app} DB cluster parameter group"
  db_cluster_parameter_group_parameters = [
    {
      name         = "rds.force_ssl"
      value        = 1
      apply_method = "pending-reboot"
    },
    {
      name         = "rds.logical_replication"
      value        = 1
      apply_method = "pending-reboot"
    },
    {
      name         = "aurora.enhanced_logical_replication"
      value        = 1
      apply_method = "pending-reboot"
    },
    {
      name         = "aurora.logical_replication_backup"
      value        = 0
      apply_method = "pending-reboot"
    },
    {
      name         = "aurora.logical_replication_globaldb"
      value        = 0
      apply_method = "pending-reboot"
    }
  ]

  create_db_parameter_group      = true
  db_parameter_group_name        = local.app
  db_parameter_group_family      = "aurora-postgresql16"
  db_parameter_group_description = "${local.app} DB parameter group"
  db_parameter_group_parameters  = []
  
  create_cloudwatch_log_group = true
  enabled_cloudwatch_logs_exports = [
    "postgresql"
  ]
  
  monitoring_interval = 10
  storage_encrypted = true
  apply_immediately = true

  tags = local.tags
}

resource "aws_ssm_parameter" "powerx_database_cluster_endpoint" {
  name  = "/${local.name}/cluster-endpoint"
  type  = "String"
  value = module.cluster.cluster_endpoint
}

resource "aws_ssm_parameter" "powerx_database_cluster_master_username" {
  name  = "/${local.name}/cluster-master-username"
  type  = "SecureString"
  value = module.cluster.cluster_master_username
}

resource "aws_ssm_parameter" "powerx_database_cluster_master_user_secret" {
  name  = "/${local.name}/cluster-master-user-secret-arn"
  type  = "String"
  value = module.cluster.cluster_master_user_secret[0].secret_arn
}

resource "aws_ssm_parameter" "powerx_database_cluster_port" {
  name  = "/${local.name}/cluster-port"
  type  = "String"
  value = module.cluster.cluster_port
}

resource "aws_ssm_parameter" "powerx_database_cluster_database_name" {
  name  = "/${local.name}/cluster-database-name"
  type  = "String"
  value = module.cluster.cluster_database_name
}

resource "aws_ssm_parameter" "powerx_database_powerx_api_user" {
  name  = "/${local.app}/powerx-api-user"
  type  = "SecureString"
  value = "powerx_api"
}

resource "random_password" "powerx_database_powerx_api_password" {
  length           = 50
  override_special = "()[]{}"
}

resource "aws_ssm_parameter" "powerx_database_powerx_api_password" {
  name  = "/${local.app}/powerx-api-password"
  type  = "SecureString"
  value = random_password.powerx_database_powerx_api_password.result
}

resource "aws_ssm_parameter" "powerx_database_alert_center_user" {
  name  = "/${local.app}/alert-center-user"
  type  = "SecureString"
  value = "alert_center"
}

resource "random_password" "powerx_database_alert_center_password" {
  length           = 50
  override_special = "()[]{}"
}

resource "aws_ssm_parameter" "powerx_database_alert_center_password" {
  name  = "/${local.app}/alert-center-password"
  type  = "SecureString"
  value = random_password.powerx_database_alert_center_password.result
}

# Docker
module "docker_image" {
  source     = "../docker_image"
  app        = local.app
  service    = local.service
  context    = "${path.module}/../../../"
  dockerfile = "Dockerfile"
}

# Secret keys
resource "random_password" "jwt_access_token_secret_key" {
  length  = 30
  special = false
}
resource "random_password" "jwt_refresh_token_secret_key" {
  length  = 30
  special = false
}

# Security groups
resource "aws_security_group" "alb_sg" {
  vpc_id      = local.vpc_id
  name_prefix = "${local.name}-alb"
  description = "${local.name} ALB security group"
  tags        = local.tags
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_security_group_rule" "alb_sg_rules" {
  for_each = {
    "HTTP web traffic (80)" = {
      from_port = 80
      to_port   = 80
      type      = "ingress"
    }
    "HTTP web traffic (443)" = {
      from_port = 443
      to_port   = 443
      type      = "ingress"
    }
    "API health check" = {
      from_port = 80
      to_port   = 80
      type      = "egress"
    }
  }
  cidr_blocks       = ["0.0.0.0/0", ]
  description       = each.key
  from_port         = each.value.from_port
  protocol          = "tcp"
  security_group_id = aws_security_group.alb_sg.id
  to_port           = each.value.to_port
  type              = each.value.type
}

# Load balancer
resource "aws_lb" "this" {
  name                                        = local.name
  internal                                    = false
  load_balancer_type                          = "application"
  security_groups                             = [aws_security_group.alb_sg.id]
  subnets                                     = local.public_subnet_ids
  enable_deletion_protection                  = false
  enable_cross_zone_load_balancing            = true
  enable_http2                                = true
  enable_tls_version_and_cipher_suite_headers = false
  enable_waf_fail_open                        = false
  enable_xff_client_port                      = true
  tags                                        = local.tags
}
resource "aws_lb_listener" "redirect" {
  load_balancer_arn = aws_lb.this.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
  tags = local.tags
}
resource "aws_lb_target_group" "this" {
  name        = local.name
  protocol    = "HTTP"
  port        = 80
  target_type = "ip"
  vpc_id      = local.vpc_id
  health_check {
    path    = "/status/ready"
    port    = 80
    matcher = "200-299"
  }
  tags = local.tags
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_acm_certificate" "this" {
  domain_name       = local.api_domain
  key_algorithm     = "RSA_2048"
  validation_method = "DNS"
  tags              = local.tags
}
resource "aws_lb_listener" "forward" {
  load_balancer_arn = aws_lb.this.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.this.arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
  tags = local.tags
}

# IAM
resource "aws_cloudwatch_log_group" "app" {
  name              = local.name
  retention_in_days = 30
  tags              = local.tags
}
resource "aws_iam_role" "task_role" {
  name = "${local.name}-container-role"
  tags = local.tags
  path = "/${local.name}/${local.service}/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
  ]
  inline_policy {
    name = "s3"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "s3:PutObject",
          ]
          Resource = [
            data.aws_s3_bucket.logo_bucket.arn,
            "${data.aws_s3_bucket.logo_bucket.arn}/*",
          ]
        },
      ]
    })
  }
  inline_policy {
    name = "${local.name}-usage-policy-timestream"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "timestream:DescribeEndpoints",
          ]
          Effect   = "Allow"
          Resource = "*"
        },
        {
          Action = [
            "timestream:Select",
          ]
          Effect = "Allow"
          Resource = [
            local.timestream_table_arn_control_zones,
            local.timestream_table_arn_temperature_places,
            local.timestream_table_arn_circuits,
            local.timestream_table_arn_pes_averages,
          ]
        },
      ]
    })
  }
}
resource "aws_iam_role" "app_task_execution" {
  name = "${local.name}-task-execution"
  tags = local.tags
  path = "/${local.name}/${local.service}/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
  ]
  inline_policy {
    name = "CloudWatch"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "logs:DescribeLogStreams"
          ]
          Resource = [
            "${aws_cloudwatch_log_group.app.arn}",
            "${aws_cloudwatch_log_group.app.arn}:*",
          ]
        }
      ]
    })
  }
  inline_policy {
    name = "SystemManager"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "ssm:GetParameters",
          ]
          Resource = [
            data.aws_ssm_parameter.dp_domain.arn,
            data.aws_ssm_parameter.dp_api_key.arn,
            data.aws_ssm_parameter.redis_host.arn,
            data.aws_ssm_parameter.redis_port.arn,
            data.aws_ssm_parameter.sendgrid_api_key.arn,
            data.aws_ssm_parameter.media_endpoint.arn,
            data.aws_ssm_parameter.media_public_key_id.arn,
            data.aws_ssm_parameter.media_private_key.arn,
            aws_ssm_parameter.powerx_database_powerx_api_user.arn,
            aws_ssm_parameter.powerx_database_powerx_api_password.arn,
          ]
        }
      ]
    })
  }
  inline_policy {
    name = "ECR"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "ecr:GetAuthorizationToken",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",
            "ecr:BatchCheckLayerAvailability",
          ]
          Resource = "*"
        }
      ]
    })
  }
}

# ECS
resource "aws_ecs_cluster" "this" {
  name = local.app
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = {
    app         = local.app
    service     = "shared"
    environment = terraform.workspace
    provisioner = "terraform"
  }
}

module "ecs_service" {
  # https://github.com/terraform-aws-modules/terraform-aws-ecs/tree/master/modules/service
  source                = "terraform-aws-modules/ecs/aws//modules/service"
  version               = "~> 5.0"
  name                  = local.name
  cluster_arn           = aws_ecs_cluster.this.arn
  cpu                   = 512
  memory                = 1024
  desired_count         = 1
  wait_for_steady_state = true
  force_new_deployment  = true

  # Container definition(s)
  create_iam_role                   = false
  create_tasks_iam_role             = false
  tasks_iam_role_arn                = aws_iam_role.task_role.arn
  create_task_exec_iam_role         = false
  create_task_exec_policy           = false
  task_exec_iam_role_arn            = aws_iam_role.app_task_execution.arn
  health_check_grace_period_seconds = 600
  runtime_platform = {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }
  container_definitions = {
    api = {
      image     = module.docker_image.name
      cpu       = 512
      memory    = 1024
      essential = true
      environment = [
        { name = "DASHBOARD_WEB_DOMAIN", value=local.dashboard_web_domain },

        { name = "JWT_ACCESS_TOKEN_SECRET_KEY", value = random_password.jwt_access_token_secret_key.result },
        { name = "JWT_REFRESH_TOKEN_SECRET_KEY", value = random_password.jwt_refresh_token_secret_key.result },

        # External Services
        { name = "POWERX_DATABASE_HOST", value = aws_ssm_parameter.powerx_database_cluster_endpoint.value },
        { name = "POWERX_DATABASE_PORT", value = aws_ssm_parameter.powerx_database_cluster_port.value },
        { name = "POWERX_DATABASE_NAME", value = aws_ssm_parameter.powerx_database_cluster_database_name.value },

        { name = "REDIS_CACHE_HOST", value = data.aws_ssm_parameter.redis_host.value },
        { name = "REDIS_CACHE_PORT", value = data.aws_ssm_parameter.redis_port.value },

        { name = "LOGO_S3_BUCKET_NAME", value = data.aws_s3_bucket.logo_bucket.bucket },
        { name = "MEDIA_BUCKET", value = data.aws_s3_bucket.logo_bucket.bucket },

        { name = "DP_PES_URL", value = "https://${data.aws_ssm_parameter.dp_domain.value}" },

        # Timestream
        { name = "TIMESTREAM_DATABASE_HVAC", value = local.timestream_database_name_hvac_data },
        { name = "TIMESTREAM_TABLE_CONTROL_ZONES", value = local.timestream_table_name_control_zones },

        { name = "TIMESTREAM_DATABASE_TEMPERATURE", value = local.timestream_database_name_temperature_data },
        { name = "TIMESTREAM_TABLE_TEMPERATURE_PLACES", value = local.timestream_table_name_temperature_places },

        { name = "TIMESTREAM_DATABASE_ELECTRICITY", value = local.timestream_database_name_electricity_data },
        { name = "TIMESTREAM_TABLE_ELECTRICITY_CIRCUITS", value = local.timestream_table_name_circuits },
        { name = "TIMESTREAM_TABLE_PES_AVERAGES", value = local.timestream_table_name_pes_averages },
      ]
      secrets = [
        { name = "MEDIA_ENDPOINT", valueFrom = data.aws_ssm_parameter.media_endpoint.name },
        { name = "MEDIA_PUBLIC_KEY_ID", valueFrom = data.aws_ssm_parameter.media_public_key_id.name },
        { name = "MEDIA_PRIVATE_KEY", valueFrom = data.aws_ssm_parameter.media_private_key.name },
        { name = "POWERX_DATABASE_USER", valueFrom = aws_ssm_parameter.powerx_database_powerx_api_user.name },
        { name = "POWERX_DATABASE_PASSWORD", valueFrom = aws_ssm_parameter.powerx_database_powerx_api_password.name },
        { name = "DP_PES_API_KEY", valueFrom = data.aws_ssm_parameter.dp_api_key.name },
        { name = "SENDGRID_API_KEY", valueFrom = data.aws_ssm_parameter.sendgrid_api_key.name },
      ]
      port_mappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
      # Example image used requires access to write to root filesystem
      readonly_root_filesystem = false

      enable_cloudwatch_logging = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-region"        = data.aws_region.this.name
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-stream-prefix" = ""
        }
      }
    }
  }
  load_balancer = {
    service = {
      target_group_arn = aws_lb_target_group.this.arn
      container_name   = "api"
      container_port   = 80
    }
  }
  subnet_ids = local.ecs_service_subnet_ids
  security_group_rules = {
    alb_ingress_80 = {
      type                     = "ingress"
      from_port                = 80
      to_port                  = 80
      protocol                 = "tcp"
      description              = "Service port"
      source_security_group_id = aws_security_group.alb_sg.id
    }
    egress_all = {
      type        = "egress"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  ignore_task_definition_changes = false
  tags                           = local.tags
}
