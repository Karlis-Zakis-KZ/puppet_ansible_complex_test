plan complex_puppet_bolt_task::configure_routers(
  TargetSpec $targets,
) {
  # Step 1: Collect interface facts
  $interfaces = run_command('show ip interface brief', $targets, '_catch_errors' => true)
  
  # Step 2: Iterate over the results and configure Ethernet1/0 if present
  $interfaces.each |$target, $result| {
    if $result['exit_code'] == 0 {
      $interface_list = $result['stdout'].split("\n")
      $has_eth1_0 = $interface_list.any |$line| { $line =~ /Ethernet1\/0/ }

      if $has_eth1_0 {
        # Assign unique IP based on target index
        $target_index = $targets.index($target)
        $ip_address = "192.168.100.${target_index + 1}"
        run_command("configure terminal", $target)
        run_command("interface Ethernet1/0", $target)
        run_command("description Configured by Puppet Bolt", $target)
        run_command("ip address ${ip_address} 255.255.255.0", $target)
        run_command("no shutdown", $target)
        run_command("end", $target)
      }
      
      # Ensure no configuration on FastEthernet ports
      $fastethernet_interfaces = $interface_list.filter |$line| { $line =~ /FastEthernet/ }
      $fastethernet_interfaces.each |$line| {
        $interface_name = $line.split()[0]
        run_command("configure terminal", $target)
        run_command("interface ${interface_name}", $target)
        run_command("description Not configured by Puppet Bolt", $target)
        run_command("end", $target)
      }
    } else {
      warning("Failed to collect interfaces for ${target.uri}: ${result['stderr']}")
    }
  }
}
