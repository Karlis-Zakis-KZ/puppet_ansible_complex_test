#!/bin/bash

INTERFACE=$PT_interface

configure terminal
interface $INTERFACE
ip address 192.168.100.$((${PT_target##*.} + 1)) 255.255.255.0
no shutdown
end
