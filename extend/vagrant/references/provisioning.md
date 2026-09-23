# Provisioning Reference

This reference is loaded on demand from ../SKILL.md.

## Shell Provisioner

```ruby
Vagrant.configure("2") do |config|
  # Inline script
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y nginx
  SHELL
  
  # External script
  config.vm.provision "shell", path: "scripts/setup.sh"
  
  # With arguments
  config.vm.provision "shell", path: "scripts/setup.sh",
    args: ["--verbose", "--env", "development"]
  
  # With environment variables
  config.vm.provision "shell", path: "scripts/setup.sh",
    env: {
      "APP_ENV" => "development",
      "DB_HOST" => "localhost"
    }
  
  # Run as non-root
  config.vm.provision "shell", path: "scripts/setup.sh",
    privileged: false
  
  # Run on specific machine
  config.vm.define "web" do |web|
    web.vm.provision "shell", inline: "echo 'Web server'"
  end
end
```

## Ansible Provisioner

```ruby
Vagrant.configure("2") do |config|
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
    ansible.inventory_path = "provisioning/inventory"
    ansible.verbose = "v"
    ansible.become = true
    
    # Extra variables
    ansible.extra_vars = {
      http_port: 80,
      db_host: "localhost"
    }
    
    # Tags
    ansible.tags = ["web", "nginx"]
    ansible.skip_tags = ["db"]
    
    # Vault
    ansible.vault_password_file = "~/.vault_pass"
    
    # Roles path
    ansible.roles_path = "provisioning/roles"
    ansible.galaxy_role_file = "provisioning/requirements.yml"
  end
end
```

## Ansible Local (runs on guest)

```ruby
Vagrant.configure("2") do |config|
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "playbook.yml"
    ansible.install_mode = "pip"
    ansible.version = "2.14.0"
    ansible.verbose = "v"
    ansible.become = true
    
    ansible.galaxy_file = "requirements.yml"
    ansible.galaxy_roles_path = "roles"
  end
end
```

## Chef Provisioner

```ruby
Vagrant.configure("2") do |config|
  config.vm.provision "chef_solo" do |chef|
    chef.cookbooks_path = "cookbooks"
    chef.roles_path = "roles"
    
    chef.add_recipe "webserver::default"
    chef.add_recipe "database::default"
    
    chef.json = {
      webserver: {
        port: 80,
        docroot: "/var/www/html"
      }
    }
  end
end
```

## Puppet Provisioner

```ruby
Vagrant.configure("2") do |config|
  config.vm.provision "puppet_apply" do |puppet|
    puppet.manifests_path = "manifests"
    puppet.manifest_file = "site.pp"
    puppet.module_path = "modules"
    
    puppet.facter = {
      "environment" => "development",
      "server_role" => "web"
    }
    
    puppet.options = ["--verbose", "--debug"]
  end
end
```

## Docker Provisioner

```ruby
Vagrant.configure("2") do |config|
  config.vm.provision "docker" do |d|
    # Pull images
    d.pull_images "nginx:latest"
    d.pull_images "postgres:14"
    
    # Run containers
    d.run "nginx",
      image: "nginx:latest",
      args: "-p 80:80 -v /vagrant/nginx.conf:/etc/nginx/nginx.conf"
    
    d.run "postgres",
      image: "postgres:14",
      args: "-e POSTGRES_PASSWORD=secret -p 5432:5432"
  end
end
```