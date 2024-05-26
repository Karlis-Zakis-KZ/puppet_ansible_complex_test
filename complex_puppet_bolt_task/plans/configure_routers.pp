plan complex_puppet_bolt_task::configure_routers (
  TargetSpec $targets,
  Integer $retries = 3
) {
  $attempts = 0
  $retry_results = []

  while $attempts < $retries {
    $attempts += 1
    $results = run_task('complex_puppet_bolt_task::get_interface_facts', $targets)

    # Log results and errors
    out::message("Attempt ${attempts}: ${results}")

    $failed_targets = $results.filter |$result| {
      $result['status'] != 'success'
    }

    if $failed_targets.empty() {
      break
    }

    # Append failed targets to retry_results
    $retry_results = $retry_results + $failed_targets.map |$failed| { $failed['target'] }

    if $attempts < $retries {
      # Sleep for a short period before retrying
      run_command('sleep 2')
    }
  }

  return $retry_results
}
