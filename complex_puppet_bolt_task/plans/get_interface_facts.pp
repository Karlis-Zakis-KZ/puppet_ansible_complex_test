plan complex_puppet_bolt_task::get_interface_facts(
  TargetSpec $targets
) {
  # Print the inventory for debugging
  out::message("Inventory: ${get_targets($targets)}")

  # Convert the TargetSpec to an array of Target objects
  $target_objects = get_targets($targets)

  # Print the target objects for debugging
  out::message("Target objects: ${target_objects}")

  # Initialize a hash to store the results
  $all_interface_facts = {}

  # Directly iterate over the target objects
  $target_objects.each |$target| {
    out::message("Target object: ${target}")

    # Command to fetch interface facts
    $command = 'show ip interface brief'

    # Run command on the target
    $result_set = run_command($command, $target, '_run_as' => 'karlis', 'password' => 'cisco')

    # Ensure that the command was successful
    if $result_set.ok {
      $result = $result_set[0]
      $interface_facts = $result['stdout']

      # Print the interface facts for debugging
      out::message("Interface facts for ${target.uri}: ${interface_facts}")

      # Update the hash using stdlib::merge function
      $all_interface_facts[$target.uri] = $interface_facts
      out::message("Updated all_interface_facts: ${all_interface_facts}")
    } else {
      out::message("Failed to fetch interface facts for ${target}.")
    }
  }

  # Output the collected interface facts as JSON
  $json_facts = stdlib::to_json($all_interface_facts)
  out::message("All interface facts: ${json_facts}")

  # Return the collected interface facts
  return $all_interface_facts
}
