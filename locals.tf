locals {
  default_tags = {
    "terraform" : true
    "project" : "epic-games-interview"
    "repo" : "https://github.com/taylorsmcclure/epic-games-interview"
  }

  user_data = <<EOF
#!/usr/bin/env bash
git clone https://github.com/taylorsmcclure/synthesize.git
./synthesize/install
cp synthesize/templates/scripts/statsite-sink-graphite.py /usr/local/sbin/statsite-sink-graphite.py
systemctl restart statsite
  EOF
}
