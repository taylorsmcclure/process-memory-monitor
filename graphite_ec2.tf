# creates a graphite/grafana stack on an EC2 instance
# https://github.com/obfuscurity/synthesize

resource "aws_security_group" "graphite_allow" {
  name        = "graphite_allow"
  description = "Allow TLS inbound traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "statsd tcp"
    from_port   = 8125
    to_port     = 8125
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "statsd udp"
    from_port   = 8125
    to_port     = 8125
    protocol    = "udp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "statsd debug proxy"
    from_port   = 8126
    to_port     = 8126
    protocol    = "udp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "TLS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  ingress {
    description = "carbon"
    from_port   = 2003
    to_port     = 2004
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.myip.body)}/32", module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.default_tags
}

resource "aws_key_pair" "ssh_public_key" {
  key_name   = "epic-games-assessment"
  public_key = data.local_file.ssh_pub_key.content

  tags = local.default_tags
}

module "graphite_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  name           = "epic-games-graphite"
  instance_count = 1

  ami                         = "ami-0e82959d4ed12de3f"
  instance_type               = "t2.small"
  key_name                    = aws_key_pair.ssh_public_key.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.graphite_allow.id]
  subnet_ids                  = module.vpc.public_subnets

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = "100"
    }
  ]

  monitoring = true
  user_data  = local.user_data

  tags = local.default_tags
}
