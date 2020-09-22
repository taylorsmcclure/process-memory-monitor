# This creates n number EC2 instances to test memory collection

resource "aws_security_group" "test_ssh" {
  name        = "test_ssh"
  description = "Allow SSH inbound traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
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

module "ec2_test_instances" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  name           = "epic-games-tests"
  instance_count = var.test_instance_count

  ami                         = "ami-0e82959d4ed12de3f"
  instance_type               = "t3a.nano"
  key_name                    = aws_key_pair.ssh_public_key.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.graphite_allow.id]
  subnet_ids                  = module.vpc.public_subnets

  monitoring = true

  tags = local.default_tags
}
