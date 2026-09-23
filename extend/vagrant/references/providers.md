# Providers Reference

This reference is loaded on demand from ../SKILL.md.

## VirtualBox Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  
  config.vm.provider "virtualbox" do |vb|
    # Basic settings
    vb.name = "my-vm"
    vb.gui = false
    vb.memory = 4096
    vb.cpus = 2
    
    # Advanced settings
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
    vb.customize ["modifyvm", :id, "--pae", "on"]
    
    # Video settings
    vb.customize ["modifyvm", :id, "--vram", "128"]
    vb.customize ["modifyvm", :id, "--accelerate3d", "on"]
    
    # Storage
    vb.customize ["storagectl", :id, "--name", "SATA Controller", "--ahci", "on"]
    
    # Network
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    
    # Clipboard
    vb.customize ["modifyvm", :id, "--clipboard", "bidirectional"]
    vb.customize ["modifyvm", :id, "--draganddrop", "bidirectional"]
  end
end
```

## VMware Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  
  config.vm.provider "vmware_fusion" do |vmw|  # macOS
    vmw.vmx["memsize"] = "4096"
    vmw.vmx["numvcpus"] = "4"
    vmw.vmx["vhv.enable"] = "TRUE"
    vmw.linked_clone = true
    vmw.gui = false
  end
  
  config.vm.provider "vmware_workstation" do |vmw|  # Linux/Windows
    vmw.vmx["memsize"] = "4096"
    vmw.vmx["numvcpus"] = "4"
  end
end
```

## Hyper-V Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "microsoft/windows-server-2022"
  
  config.vm.provider "hyperv" do |hv|
    hv.memory = 4096
    hv.maxmemory = 8192
    hv.cpus = 2
    hv.enable_virtualization_extensions = true
    hv.enable_checkpoints = true
    hv.vmname = "dev-vm"
    hv.vlan_id = 100
    hv.ip_address_timeout = 180
  end
end
```

## libvirt Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2204"
  
  config.vm.provider :libvirt do |libvirt|
    libvirt.cpus = 4
    libvirt.memory = 4096
    libvirt.driver = "kvm"
    libvirt.cpu_mode = "host-passthrough"
    libvirt.disk_bus = "virtio"
    libvirt.disk_driver :cache => "none", :io => "native"
    libvirt.video_type = "qxl"
    libvirt.video_vram = "128"
    libvirt.interface_type = "bridge"
    libvirt.interface_source = "br0"
  end
end
```

## AWS Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "aws"
  
  config.vm.provider :aws do |aws, override|
    override.ssh.username = "ec2-user"
    override.ssh.private_key_path = "~/.ssh/my-key.pem"
    
    aws.access_key_id = ENV['AWS_ACCESS_KEY_ID']
    aws.secret_access_key = ENV['AWS_SECRET_ACCESS_KEY']
    aws.region = "us-east-1"
    aws.ami = "ami-0c55b159cbfafe1f0"
    aws.instance_type = "t3.medium"
    aws.keypair_name = "my-key"
    aws.security_groups = ["default"]
    
    aws.tags = {
      'Name' => 'vagrant-dev',
      'Environment' => 'development'
    }
    
    aws.block_device_mappings = [{
      device_name: '/dev/sda1',
      ebs: {
        volume_size: 50,
        volume_type: 'gp3',
        delete_on_termination: true
      }
    }]
  end
end
```

## DigitalOcean Provider

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "digitalocean"
  
  config.vm.provider :digital_ocean do |provider|
    provider.access_token = ENV['DIGITALOCEAN_ACCESS_TOKEN']
    provider.ssh_key_id = "12345678"
    provider.image = "ubuntu-22-04-x64"
    provider.size = "s-2vcpu-4gb"
    provider.region = "nyc3"
    provider.ssh_username = "root"
    provider.private_networking = true
    provider.tags = ["vagrant", "development"]
  end
end
```