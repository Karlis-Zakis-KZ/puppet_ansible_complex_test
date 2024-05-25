plan bolt_module::configure_banner(
  TargetSpec $targets
) {
  $banner_command = "banner login ^C\nWelcome to the router! Unauthorized access is prohibited.^C"

  $targets.each |$target| {
    out::message("Configuring banner on ${target.uri}")

    $commands = [
      "configure terminal",
      $banner_command,
      "end",
      "write memory"
    ]

    $commands.each |$cmd| {
      $output = run_command($cmd, $target)
      out::message("Output for command '${cmd}': ${$output['stdout']}")
    }
  }
}
