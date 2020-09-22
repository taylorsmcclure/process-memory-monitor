module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "epic-interview"
  cidr = "10.2.0.0/16"

  azs             = ["us-east-2a", "us-east-2b", "us-east-2c"]
  private_subnets = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
  public_subnets  = ["10.2.101.0/24", "10.2.102.0/24", "10.2.103.0/24"]

  tags = local.default_tags
}
