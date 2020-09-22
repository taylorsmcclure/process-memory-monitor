# gets your public IP so you are on the allow list
data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

# your local public key file
data "local_file" "ssh_pub_key" {
  filename = "epic-interview.pub"
}
