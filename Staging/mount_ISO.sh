unzip -o image_$1.zip

DEV=`losetup -f`

losetup -P $DEV $1.zip

mount ${DEV}p2 /mnt/WaziGate_nightly
mount ${DEV}p1 /mnt/WaziGate_nightly/boot
echo "console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=172.16.11.191:/mnt/WaziGate_nightly,vers=3 rw ip=dhcp rootwait elevator=deadline" > /mnt/WaziGate_nightly/boot/cmdline.txt
echo "" > /mnt/WaziGate_nightly/etc/fstab

