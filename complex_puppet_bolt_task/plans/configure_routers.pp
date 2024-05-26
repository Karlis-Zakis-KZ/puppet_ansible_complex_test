plan complex_puppet_bolt_task::configure_routers(
  TargetSpec $targets,
  String $ethernet_interface = 'Ethernet1/0'
) {
  # Connect to each target and collect facts
  $results = run_task('complex_puppet_bolt_task::get_interface_facts', $targets)

  $results.each |$result| {
    $target = $result['target']
    $facts = $result['value']['stdout']

    # Check if Ethernet1/0 is present
    if $facts =~ /$ethernet_interface/ {
      run_task('complex_puppet_bolt_task::configure_interface', $target, interface => $ethernet_interface)
    }

    # Ensure no configuration on FastEthernet ports
    $facts.scan(/FastEthernet[0-9]+\/[0-9]+/).each |$fast_interface| {
      run_task('complex_puppet_bolt_task::clear_interface', $target, interface => $fast_interface)
    }
  }
}
