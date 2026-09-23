---
name: vagrant
description: Use when managing Vagrant VM environments - Vagrantfile configuration, providers like VirtualBox and libvirt, provisioners (shell, Ansible, Chef, Puppet, Docker), multi-machine setups, networking, synced folders, custom boxes, plugins, or triggers
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - vagrant
    - virtualization
    - devops
    - development-environment
    - virtualbox
    - infrastructure
    - ansible
---

# Vagrant Development

Complete guide for managing virtual machine environments with Vagrant.

## Overview

Vagrant is a tool for building and managing virtual machine environments in a single, consistent workflow.

**Key Characteristics:**
- Reproducible environments
- Multiple providers (VirtualBox, VMware, Docker)
- Provisioners (Shell, Ansible, Chef, Puppet)
- Multi-machine support
- Portable boxes

## Installation

### Install Vagrant

```bash
# macOS (Homebrew)
brew install hashicorp/tap/hashicorp-vagrant

# Ubuntu/Debian
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install vagrant

# Windows (Chocolatey)
choco install vagrant

# Or download from https://www.vagrantup.com/downloads
```

### Install Provider

```bash
# VirtualBox (most common)
# macOS: brew install --cask virtualbox
# Ubuntu: sudo apt install virtualbox
# Windows: choco install virtualbox

# VMware (requires license)
vagrant plugin install vagrant-vmware-desktop

# Hyper-V (Windows only)
# Enable in Windows Features

# libvirt (Linux)
vagrant plugin install vagrant-libvirt
```

## Basic Vagrantfile

### Minimal Configuration

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.hostname = "myvm"
  
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end
end
```

### Complete Configuration

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|
  # Base box
  config.vm.box = "ubuntu/focal64"
  config.vm.box_version = ">= 202310.0.0"
  config.vm.hostname = "dev-environment"
  
  # Network configuration
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 8443
  
  # Synced folders
  config.vm.synced_folder "./app", "/var/www/html"
  config.vm.synced_folder "./data", "/data", disabled: false
  
  # VirtualBox provider
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
    vb.name = "my-dev-vm"
    vb.gui = false
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
  
  # Shell provisioner
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y apache2 mysql-server php
  SHELL
  
  # Ansible provisioner
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
    ansible.become = true
  end
end
```

## Common Commands

```bash
# Create Vagrantfile
vagrant init ubuntu/focal64

# Start VM
vagrant up

# SSH into VM
vagrant ssh

# Stop VM
vagrant halt

# Restart VM
vagrant reload

# Destroy VM
vagrant destroy

# Suspend VM
vagrant suspend

# Resume VM
vagrant resume

# Status
vagrant status

# Global status
vagrant global-status

# Box management
vagrant box list
vagrant box add ubuntu/focal64
vagrant box remove ubuntu/focal64
vagrant box update
vagrant box outdated

# Plugin management
vagrant plugin list
vagrant plugin install vagrant-vbguest
vagrant plugin uninstall vagrant-vbguest

# Validate Vagrantfile
vagrant validate

# SSH config
vagrant ssh-config

# Package box
vagrant package --output my-custom.box
```

## Networking

### Private Networks

```ruby
Vagrant.configure("2") do |config|
  # Static IP
  config.vm.network "private_network", ip: "192.168.33.10"
  
  # With netmask
  config.vm.network "private_network", 
    ip: "192.168.33.10",
    netmask: "255.255.255.0"
  
  # DHCP
  config.vm.network "private_network", type: "dhcp"
  
  # Internal network (isolated)
  config.vm.network "private_network",
    ip: "10.0.0.10",
    virtualbox__intnet: "internal_network"
end
```

### Public Networks (Bridged)

```ruby
Vagrant.configure("2") do |config|
  # Bridge to specific interface
  config.vm.network "public_network",
    bridge: "en0: Wi-Fi (AirPort)"
  
  # With static IP
  config.vm.network "public_network",
    bridge: "en0",
    ip: "192.168.1.100"
  
  # Auto-bridge (prompts to select)
  config.vm.network "public_network"
end
```

### Port Forwarding

```ruby
Vagrant.configure("2") do |config|
  # Basic port forwarding
  config.vm.network "forwarded_port", guest: 80, host: 8080
  
  # With auto-correction
  config.vm.network "forwarded_port",
    guest: 80,
    host: 8080,
    auto_correct: true
  
  # UDP
  config.vm.network "forwarded_port",
    guest: 53,
    host: 1053,
    protocol: "udp"
  
  # Multiple ports
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 443, host: 8443
  config.vm.network "forwarded_port", guest: 3306, host: 3306
end
```

## Synced Folders

### VirtualBox Shared Folders (Default)

```ruby
Vagrant.configure("2") do |config|
  config.vm.synced_folder "./app", "/var/www/html"
  
  # Disable default
  config.vm.synced_folder ".", "/vagrant", disabled: true
  
  # With options
  config.vm.synced_folder "./app", "/var/www/html",
    owner: "www-data",
    group: "www-data",
    mount_options: ["dmode=775", "fmode=664"]
end
```

### NFS (Better Performance)

```ruby
Vagrant.configure("2") do |config|
  config.vm.synced_folder "./app", "/var/www/html",
    type: "nfs",
    nfs_udp: false,
    mount_options: [
      "nfsvers=3",
      "tcp",
      "rsize=32768",
      "wsize=32768"
    ]
end
```

### RSync

```ruby
Vagrant.configure("2") do |config|
  config.vm.synced_folder "./app", "/var/www/html",
    type: "rsync",
    rsync__auto: true,
    rsync__exclude: [".git/", "node_modules/", "*.log"],
    rsync__args: ["--verbose", "--archive", "--delete", "-z"]
end
```

### SMB (Windows)

```ruby
Vagrant.configure("2") do |config|
  config.vm.synced_folder "./app", "/var/www/html",
    type: "smb",
    smb_host: "127.0.0.1",
    smb_username: ENV['USER'],
    smb_password: ENV['SMB_PASSWORD']
end
```

## Triggers

### Basic Triggers

```ruby
Vagrant.configure("2") do |config|
  config.trigger.before :up do |trigger|
    trigger.name = "Before Up"
    trigger.info = "Starting VM..."
  end
  
  config.trigger.after :up do |trigger|
    trigger.name = "After Up"
    trigger.run = {inline: "echo 'VM is ready!'"}
  end
  
  config.trigger.before :destroy do |trigger|
    trigger.name = "Confirm Destroy"
    trigger.ask = "Are you sure you want to destroy?"
  end
end
```

### Advanced Triggers

```ruby
Vagrant.configure("2") do |config|
  # Run commands on host
  config.trigger.after :up do |trigger|
    trigger.run = {
      inline: "echo 'VM IP:' && vagrant ssh -c 'ip addr show eth1'"
    }
  end
  
  # Run commands on guest
  config.trigger.after :provision do |trigger|
    trigger.run_remote = {
      inline: "systemctl status nginx"
    }
  end
  
  # Execute only on specific machine
  config.vm.define "web" do |web|
    web.trigger.after :up do |trigger|
      trigger.info = "Web server is up!"
    end
  end
end
```

## Best Practices

1. **Version control your Vagrantfile**
2. **Use specific box versions** for reproducibility
3. **Use provisioners** for repeatable setup
4. **Enable auto_correct** for port forwarding
5. **Use triggers** for automation hooks
6. **Document custom boxes** with README
7. **Test multi-machine** setups thoroughly
8. **Use NFS** for better synced folder performance
9. **Keep Vagrant updated**
10. **Clean up unused boxes** regularly

## Resources

- **Documentation:** https://www.vagrantup.com/docs
- **Box Catalog:** https://app.vagrantup.com/boxes/search
- **GitHub:** https://github.com/hashicorp/vagrant
- **Community:** https://discuss.hashicorp.com/c/vagrant

## Quick Reference

### Common Vagrantfile Patterns

```ruby
# Basic
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.synced_folder ".", "/vagrant"
end

# With provisioning
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.provision "shell", path: "setup.sh"
end

# Multi-machine
Vagrant.configure("2") do |config|
  config.vm.define "web"
  config.vm.define "db"
end
```

### Common Commands

```bash
vagrant up              # Start VM
vagrant ssh             # SSH into VM
vagrant halt            # Stop VM
vagrant destroy         # Delete VM
vagrant reload          # Restart with new config
vagrant provision       # Run provisioners
vagrant status          # Show status
vagrant global-status   # All VMs
vagrant box list        # List boxes
vagrant plugin list     # List plugins
```

## Deep Dives

Load these reference files for detailed topics:

- **Providers** — VirtualBox, VMware, Hyper-V, libvirt, AWS, DigitalOcean configuration → `references/providers.md`
- **Provisioning** — Shell, Ansible, Ansible Local, Chef, Puppet, Docker provisioners → `references/provisioning.md`
- **Multi-Machine** — Complex multi-VM setups with dependencies → `references/multi-machine.md`
- **Boxes & Plugins** — Custom box packaging and plugin management → `references/boxes-plugins.md`
- **Troubleshooting & Performance** — Debugging and optimization → `references/troubleshooting.md`