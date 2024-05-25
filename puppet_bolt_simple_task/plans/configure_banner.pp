plan bolt_module::configure_banner(
  TargetSpec $targets
) {
  $motd_messages = [
    "Attention! Scheduled maintenance on this device.",
    "Warning! Unscheduled maintenance may occur on this device.",
    "Notice: Routine check on this device today.",
    "Reminder: This device will be updated soon."
  ]

  $targets.each |$target| {
    $motd_message = $motd_messages.get(random($motd_messages.size))
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
