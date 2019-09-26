lvm_extend
==========

Ansible role which helps to create and extend LVM logical volumes over one or
more LVM physical volumes.

This role only supports creation and extension of VG. By default, it extends
the logical volume over all physical volumes. Custom physical volume can be
specified by the `pv` parameter of the configuration (see examples). Only swap,
EXT2/3/4 and XFS filesystems are currently supported. This role must be run as
root or via sudo (`--become`).

The configuration of the role is done in such way that it should not be necessary
to change the role for any kind of configuration. All can be done either by
changing role parameters or by declaring completely new configuration as a
variable. That makes this role absolutely universal. See the examples below for
more details.

Please report any issues or send PR.


Examples
--------

```yaml
---

- name: Example of how to use this role
  hosts: all
  vars:
    lvm_extend_config:
      # This is the VG name
      vg_os:
        # List of disks from /dev which should be associated with the VG
        disks:
          # This is the empty disk which will be added into the VG
          - sdb
        # List of volumes
        vols:
          # The name corresponds with /dev/vg_os/swap
          - name: swap
            # Resize to 2G
            size: 2G
            # Filesystem type [swap | ext | xfs] - see lvm_extend_default_fs_type for default
            type: swap
          # Resize the root partition using EXT 2/3/4 to fill the rest of the space
          # The name corresponds with /dev/vg_os/root
          - name: root
      # Optionally define another VG (will be created if doesn't exist)
      vg_data:
        # List of empty disks
        disks:
          - sdc
          - sdd
        vols:
          # The name corresponds with /dev/vg_data/app1
          - name: app1
            # Resize to 10G
            size: 10G
            # Use only /dev/sdc1 PV
            pv: sdc1
            # Mount the volume to /mnt/app1
            mount: yes
          # Resize the app2 partition using EXT 2/3/4 to fill the rest of the space
          # The name corresponds with /dev/vg_data/app2
          # Use all PVs (/dev/sdc1 and /dev/sdd1)
          - name: app2
            # Custom mount details
            mount:
              dir: /mnt/app2_data
              opts: defaults,auto,rw
  roles:
    - lvm_exptend
```

If something goes wrong before the filesystem resizing finished, you can fix it
by removing the physical volume (`pvremove /dev/sdX`), removing the disk
partitions (`for CMD in d w; do echo $CMD; done | fdisk /dev/sdX`) and starting
the process again.


Role variables
--------------

```yaml
# Package containing LVM tools
lvm_extend_pkg: lvm2

# Default set of LVM logical vlumes to be extended
lvm_extend_config__default: {}
# Example:
#lvm_extend_config__default:
#  # This is the VG name
#  vg_os:
#    # List of disks from /dev which should be associated with the VG
#    disks:
#      # This is the empty disk which will be added into the VG
#      - sdb
#    # List of volumes
#    vols:
#      # The name corresponds with /dev/vg_os/swap
#      - name: swap
#        # Resize to 2G
#        size: 2G
#        # Filesystem type [swap | ext | xfs] - see lvm_extend_default_fs for default
#        type: swap
#      # Resize the root partition using EXT 2/3/4 to fill the rest of the space
#      # The name corresponds with /dev/vg_os/root
#      - name: root

# Custom set of LVM logical volumes to be extended
lvm_extend_config__custom: {}

# Final set of LVM logical volumes to be extended
lvm_extend_config: "{{
  lvm_extend_config__default | combine(
  lvm_extend_config__custom) }}"

# Disk pattern used to detect empty disks
lvm_extend_cmd_new_disks_pattern: sd.*

# Command to get list of empty disks
lvm_extend_cmd_new: >
  cat /proc/partitions |
  grep -P '^\s+\d+\s+\d+\s+\d+\s+{{ lvm_extend_cmd_new_disks_pattern }}' |
  awk '{print $4}' |
  sed 's/[0-9]//' |
  sort |
  uniq -c |
  grep '^\s*1\s' |
  sed 's/.*\s//'

lvm_extend_cmd_detect_vg: >
  {{ lvm_extend_cmd_vgdisplay }} -cA | egrep '^\s*{{ lvm_extend_vg.key }}'

# Command to create LVM physical volume
lvm_extend_cmd_fdisk: /sbin/fdisk

# Command to crate LVM partition on the disk
lvm_extend_cmd_partition: >-
  for CMD in n p 1 '' '' t 8e w; do
    echo $CMD;
  done | {{ lvm_extend_cmd_fdisk }}

# Command to create LVM physical volume
lvm_extend_cmd_pvcreate: /sbin/pvcreate

# Command to create the LVM volume group
lvm_extend_cmd_vgcreate: /sbin/vgcreate

# Command to extend the LVM volume group
lvm_extend_cmd_vgextend: /sbin/vgextend

# Command to display LVM volume groups
lvm_extend_cmd_vgdisplay: /sbin/vgdisplay

# Command to create the LVM logical volume
lvm_extend_cmd_lvcreate: /sbin/lvcreate

# Command to extend the LVM logical volume
lvm_extend_cmd_lvextend: /sbin/lvextend

# Commands required for the swap resizing
lvm_extend_cmd_mkswap: /sbin/mkswap
lvm_extend_cmd_swapoff: /sbin/swapoff
lvm_extend_cmd_swapon: /sbin/swapon

# Command to create EXT 2/3/4 filesystem
lvm_extend_cmd_create_ext: /sbin/mkfs.ext4

# Command to create XFS filesystem
lvm_extend_cmd_create_xfs: /sbin/mkfs.xfs

# Data structure allowing to pick the right tool for FS creation
lvm_extend_cmd_create:
  ext: "{{ lvm_extend_cmd_create_ext }}"
  xfs: "{{ lvm_extend_cmd_create_xfs }}"

# Command to grow EXT 2/3/4 filesystem
lvm_extend_cmd_grow_ext: /sbin/resize2fs

# Command to grow XFS filesystem
lvm_extend_cmd_grow_xfs: /sbin/xfs_growfs

lvm_extend_cmd_mountpoint: >
  env mount -l | grep '^/dev/mapper/%s-%s\s' | head -n1 | cut -f3 -d' '

# Data structure allowing to pick the right tool fro FS growing
lvm_extend_cmd_grow:
  ext: "{{ lvm_extend_cmd_grow_ext }}"
  xfs: "{{ lvm_extend_cmd_grow_xfs }}"

# Default filesystem type
lvm_extend_default_fs_type: "{{
  'xfs'
    if (
      (
        ansible_facts.os_family == 'RedHat' and
        ansible_facts.distribution_major_version | int >= 7
      ) or (
        ansible_facts.distribution == 'Ubuntu' and
        ansible_facts.distribution_major_version | int >= 16
      )
    )
    else
  'ext'
}}"

# Default mount options
lvm_extend_mount_opts: defaults
```


License
-------

MIT


Author
------

Jiri Tyr
