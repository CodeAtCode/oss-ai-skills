# Troubleshooting & Performance Reference

This reference is loaded on demand from ../SKILL.md.

## Troubleshooting

### Common Errors

#### SSH Timeout

```ruby
Vagrant.configure("2") do |config|
  # Increase SSH timeout
  config.ssh.timeout = 120
  config.ssh.insert_key = false
  
  # For slow networks
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end
end
```

#### Network Issues

```bash
# Debug network
vagrant ssh -c "ip addr show"
vagrant ssh -c "cat /etc/network/interfaces"

# Reload network
vagrant reload

# Check VirtualBox networks
VBoxManage list natnets
VBoxManage list hostonlyifs
```

#### Synced Folder Permission Denied

```ruby
config.vm.synced_folder "./app", "/var/www/html",
  owner: "vagrant",
  group: "vagrant",
  mount_options: ["dmode=775", "fmode=664"]
```

#### Box Download Issues

```bash
# Clean download cache
rm -rf ~/.vagrant.d/tmp/*

# Download with specific version
vagrant box add ubuntu/focal64 --box-version 202310.0.0

# Use alternative download location
export VAGRANT_SERVER_URL="https://vagrantcloud.com"
```

### Debug Mode

```bash
# Enable debug logging
VAGRANT_LOG=debug vagrant up

# Enable info logging
VAGRANT_LOG=info vagrant up

# Debug specific plugin
VAGRANT_LOG=debug VAGRANT_DEFAULT_PROVIDER=virtualbox vagrant up
```

### Reset Environment

```bash
# Destroy all VMs
vagrant destroy -f

# Remove cached box
vagrant box remove ubuntu/focal64

# Clean up
rm -rf .vagrant
rm -rf ~/.vagrant.d/data

# Fresh start
vagrant up
```

## Performance Optimization

### VirtualBox Optimization

```ruby
Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |vb|
    # Memory and CPU
    vb.memory = 4096
    vb.cpus = 2
    
    # Enable PAE/NX
    vb.pae = true
    
    # I/O optimization
    vb.customize ["storagectl", :id, "--name", "SATA Controller", "--ahci", "on"]
    vb.customize ["storageattach", :id, "--storagectl", "SATA Controller",
                  "--type", "hdd", "--nonrotational", "on"]
    
    # Network optimization
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    
    # Disable audio (saves resources)
    vb.customize ["modifyvm", :id, "--audio", "none"]
  end
  
  # Use NFS for better disk I/O
  config.vm.synced_folder "./app", "/app", type: "nfs"
end
```

### Parallel Operations

```ruby
# Enable parallel execution
Vagrant.configure("2") do |config|
  # Machines can be started in parallel
  config.vm.define "web"
  config.vm.define "db"
  
  # Use provisioner ordering
  config.vm.provision "shell", inline: "apt-get update", run: "always"
end
```