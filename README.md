lvm_extend
===============

Ansible role which helps to extend LVM logical volumes over one or more LVM
physical volumes.

This role only supports extension inside one VG only. By default, it extends the
logical volume over all physical volumes. Custom physical volume can be
specified by the `pv` parameter of the configuration (see examples). Only swap
and EXT2/3/4 filesystems are currently supported. This role requires to be run
as root or via sudo (`--become`).


Examples
--------

```
---

- name: Example of how to use this role
  hosts: all
  vars:
    # Desired swap LV size
    lvm_extend_swap_size: 2G

    # LV configuration
    lvm_extend_config:
      - path: /dev/mapper/{{ lvm_extend_vg }}-swap
        size: "{{ lvm_extend_swap_size }}"
        type: swap
      - path: "/dev/mapper/{{ lvm_extend_vg }}-root"
        type: ext
  roles:
    - lvm_disk_exptend

- name: Example of how to specify custom LVM volume group name
  hosts: all
  vars:
    # Autodetection works well if there is only one VG.
    # If there is more VGs, we can define the correct one like this:
    lvm_extend_vg: vg1

    # Desired swap LV size
    lvm_extend_swap_size: 2G

    # LV configuration
    lvm_extend_config:
      - path: /dev/mapper/{{ lvm_extend_vg }}-swap
        size: "{{ lvm_extend_swap_size }}"
        type: swap
      - path: "/dev/mapper/{{ lvm_extend_vg }}-root"
        type: ext
  roles:
    - lvm_extend

- name: Example of how to specify a physical volume to extend the logical volume over
  hosts: all
  vars:
    # Desired swap LV size
    lvm_extend_swap_size: 2G

    # LV configuration
    lvm_extend_config:
      - path: /dev/mapper/{{ lvm_extend_vg }}-swap
        size: "{{ lvm_extend_swap_size }}"
        # Swap PV will extend only over the /dev/sdb1
        pv: /dev/sdb1
        type: swap
        # Root PV will extend over all other LVs
      - path: "/dev/mapper/{{ lvm_extend_vg }}-root"
        type: ext
  roles:
    - lvm_extend
```

If something goes wrong before the filesystem resizing finished, you can fix it
by removing the physical volume (`pvremove /dev/sdX`), removing the disk
partitions (`for CMD in d w; do echo $N; done | fdisk /dev/sdX`) and starting
the process again.


Role variables
--------------

```
# Name of the LVM volume group (autodetected by default)
lvm_extend_vg: null

# Default set of LVM logical vlumes to be extended
lvm_extend_config__default: []
# Example:
#lvm_extend_config__default:
#  # Make the swap partition 2GB big
#  - path: /dev/mapper/{{ lvm_extend_vg }}-swap
#    size: 2G
#    type: swap
#  # If no size specified (only once), it will extend to 100% of the free space
#  - lv: /dev/mapper/{{ lvm_extend_vg }}-root
#    type: ext

# Custom set of LVM logical volumes to be extended
lvm_extend_config__custom: []

# Final set of LVM logical volumes to be extended
lvm_extend_config: "{{
  lvm_extend_config__default +
  lvm_extend_config__custom }}"

# Command to identify the LVM volume group name
lvm_extend_cmd_autodetect: >
  {{ lvm_extend_cmd_vgdisplay }} -cA |
  grep -Po '(?<=  ).[^:]*' |
  head -n1

# Command to get list of new disks
lvm_extend_cmd_new: >
  cat /proc/partitions |
  grep -P '^\s+\d+\s+\d+\s+\d+\s+sd.*' |
  awk '{print $4}' |
  sed 's/[0-9]//' |
  sort |
  uniq -c |
  grep '^\s*1\s' |
  sed 's/.*\s//'

# Command to create LVM physical volume
lvm_extend_cmd_fdisk: /sbin/fdisk

# Command to crate LVM partition on the disk
lvm_extend_cmd_partition: >-
  for CMD in n p 1 '' '' t 8e w; do
    echo $CMD;
  done | {{ lvm_extend_cmd_fdisk }}

# Command to create LVM physical volume
lvm_extend_cmd_pv: /sbin/pvcreate

# Command to extend the LVM volume group
lvm_extend_cmd_vg: /sbin/vgextend

# Command to display LVM volume groups
lvm_extend_cmd_vgdisplay: /sbin/vgdisplay

# Command to extend the LVM logical volume
lvm_extend_cmd_lv: /sbin/lvextend

# Commands required for the swap resizing
lvm_extend_cmd_mkswap: /sbin/mkswap
lvm_extend_cmd_swapoff: /sbin/swapoff
lvm_extend_cmd_swapon: /sbin/swapon

# Command to resize filesystem on a EXT2/3/4 partition
lvm_extend_cmd_resize_ext: /sbin/resize2fs
```


License
-------

MIT


Author
------

Jiri Tyr
