#!/bin/bash

ifconfig | grep -m 1 inet >> /home/$USER/ip_address.txt

rclone sync /home/$USER/ip_address.txt GoogleDrive:/
