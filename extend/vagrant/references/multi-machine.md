# Multi-Machine Reference

This reference is loaded on demand from ../SKILL.md.

## Basic Multi-Machine

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  
  config.vm.define "web" do |web|
    web.vm.hostname = "web"
    web.vm.network "private_network", ip: "192.168.33.10"
    web.vm.network "forwarded_port", guest: 80, host: 8080
    
    web.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
    end
    
    web.vm.provision "shell", inline: "apt-get install -y nginx"
  end
  
  config.vm.define "db" do |db|
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.33.20"
    
    db.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
    end
    
    db.vm.provision "shell", inline: "apt-get install -y postgresql"
  end
end
```

## Complex Multi-Machine with Dependencies

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  
  # Primary machine (default)
  config.vm.define "loadbalancer", primary: true do |lb|
    lb.vm.hostname = "lb"
    lb.vm.network "private_network", ip: "192.168.33.10"
    lb.vm.network "forwarded_port", guest: 80, host: 8080
    
    lb.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end
    
    lb.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y haproxy
    SHELL
  end
  
  # Web servers
  (1..3).each do |i|
    config.vm.define "web#{i}" do |web|
      web.vm.hostname = "web#{i}"
      web.vm.network "private_network", ip: "192.168.33.#{20 + i}"
      
      web.vm.provider "virtualbox" do |vb|
        vb.memory = "2048"
      end
      
      web.vm.provision "shell", inline: <<-SHELL
        apt-get update
        apt-get install -y nginx
        echo "Web Server #{i}" > /var/www/html/index.html
      SHELL
      
      # Only start after loadbalancer
      web.vm.provision "shell", run: "never" do |s|
        s.inline = "echo 'Web#{i} ready'"
      end
    end
  end
  
  # Database
  config.vm.define "database" do |db|
    db.vm.hostname = "db"
    db.vm.network "private_network", ip: "192.168.33.50"
    
    db.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
    end
    
    db.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y postgresql
      systemctl start postgresql
    SHELL
  end
end
```

## Control Commands

```bash
# Start all machines
vagrant up

# Start specific machine
vagrant up web

# Start multiple machines
vagrant up web db

# SSH to specific machine
vagrant ssh web

# Provision specific machine
vagrant provision web

# Reload specific machine
vagrant reload web

# Destroy specific machine
vagrant destroy web
```