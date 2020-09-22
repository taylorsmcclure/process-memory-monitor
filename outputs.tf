output "graphite_ec2_public_ip" {
  value       = module.graphite_ec2.public_ip
  description = "public IP for the grahite stack"
}

output "test_instance_public_ips" {
  value       = module.ec2_test_instances.public_ip
  description = "public IPs for the ec2 test instances"
}

output "graphite_url" {
  value = "https://${module.graphite_ec2.public_ip[0]}"
}

output "grafana_url" {
  value = "http://${module.graphite_ec2.public_ip[0]}:3000"
}

output "grafana_username" {
  value = "admin"
}

output "grafana_password" {
  value = "admin"
}