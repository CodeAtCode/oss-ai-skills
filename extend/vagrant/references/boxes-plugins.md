# Boxes & Plugins Reference

This reference is loaded on demand from ../SKILL.md.

## Custom Boxes

### Packaging a Box

```bash
# From running VM
vagrant package --base my-configured-vm --output my-custom.box

# With Vagrantfile template
vagrant package --base my-vm --output my.box --vagrantfile Vagrantfile.template

# With include files
vagrant package --base my-vm --output my.box --include README.md,metadata.json
```

### metadata.json

```json
{
  "name": "myorg/ubuntu-custom",
  "description": "Custom Ubuntu 20.04 with pre-installed tools",
  "versions": [
    {
      "version": "1.0.0",
      "providers": [
        {
          "name": "virtualbox",
          "url": "https://example.com/boxes/ubuntu-custom-1.0.0.box",
          "checksum": "sha256:abc123...",
          "checksum_type": "sha256"
        }
      ]
    }
  ]
}
```

### Adding and Using Custom Boxes

```bash
# Add local box
vagrant box add myorg/ubuntu-custom ./my-custom.box

# Add from URL
vagrant box add myorg/ubuntu-custom https://example.com/my-custom.box

# Use in Vagrantfile
# config.vm.box = "myorg/ubuntu-custom"

# List boxes
vagrant box list

# Update box
vagrant box update --box myorg/ubuntu-custom

# Remove box
vagrant box remove myorg/ubuntu-custom
```

### Publishing to Vagrant Cloud

```bash
# Login
vagrant cloud auth login

# Publish
vagrant cloud publish myorg/ubuntu-custom 1.0.0 \
  --description "Custom Ubuntu with development tools" \
  --provider virtualbox \
  --file ./my-custom.box
```

## Plugins

### Installing Plugins

```bash
# Install plugin
vagrant plugin install vagrant-vbguest

# Install specific version
vagrant plugin install vagrant-vbguest --plugin-version 0.21.0

# List installed plugins
vagrant plugin list

# Update plugin
vagrant plugin update vagrant-vbguest

# Uninstall plugin
vagrant plugin uninstall vagrant-vbguest
```

### Useful Plugins

```bash
# VirtualBox Guest Additions
vagrant plugin install vagrant-vbguest

# Host Manager (manages /etc/hosts)
vagrant plugin install vagrant-hostmanager

# Disk size management
vagrant plugin install vagrant-disksize

# Snapshot management
vagrant plugin install vagrant-snapshot

# Cachier (package cache)
vagrant plugin install vagrant-cachier
```

### Plugin Configuration

```ruby
# vagrant-vbguest
config.vbguest.auto_update = true
config.vbguest.no_remote = true

# vagrant-hostmanager
config.hostmanager.enabled = true
config.hostmanager.manage_host = true
config.hostmanager.manage_guest = true

# vagrant-disksize
config.disksize.size = '50GB'
```