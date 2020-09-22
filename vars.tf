variable "aws_access_key" {
  type        = string
  description = "AWS access key that terraform can use"
}

variable "aws_secret_key" {
  type        = string
  description = "AWS secret key that terraform can use"
}

variable "test_instance_count" {
  default     = 5
  description = "(optional) number of test EC2 instances to launch"
}
