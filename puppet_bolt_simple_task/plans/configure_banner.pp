plan puppet_bolt_simple_task::configure_banner(
  TargetSpec $targets
) {
  # Run the command and get the result
  $result_set = run_command('/home/osboxes/puppet_ansible_complex_test/puppet_bolt_simple_task/scripts/generate_motd.py', 'localhost')
  
  # Ensure that the command was successful and get the first result
  if $result_set.ok {
    $result = $result_set[0]
    $motd_message = parsejson($result['stdout'])['motd_message']

    $targets.each |$target| {
      # Print the target object
      out::message("Target object: ${target}")

      # Placeholder for the actual commands
      out::message("Applying MOTD message to target: ${motd_message}")
    }
  } else {
    out::message("Failed to generate MOTD message. Command failed on localhost.")
  }
}
