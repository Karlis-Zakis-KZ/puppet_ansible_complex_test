plan puppet_bolt_simple_task::configure_banner(
  TargetSpec $targets
) {
  $result = run_command('/home/osboxes/puppet_ansible_complex_test/puppet_bolt_simple_task/scripts/generate_motd.py', 'localhost')
  $motd_message = parsejson($result['stdout'])['motd_message']

  $targets.each |$target| {
    out::message("Applying MOTD message to ${target.uri}: ${motd_message}")

    $commands = [
      'configure terminal',
      "banner motd $ ${motd_message} $",
      'end'
    ]

    $commands.each |$command| {
      run_command($command, $target, '_run_as' => 'karlis', 'password' => 'cisco')
    }
  }
}
