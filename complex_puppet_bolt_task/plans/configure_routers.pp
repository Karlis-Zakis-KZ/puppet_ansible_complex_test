plan complex_puppet_bolt_task::configure_routers(
  TargetSpec $targets,
  Integer $retries = 3,
  Integer $delay = 5
) {
  $results = run_task('complex_puppet_bolt_task::get_interface_facts', $targets)
  $failures = $results.error_set

  if $failures {
    notice("Initial task run failed on ${failures.length} targets. Retrying...")

    $attempt = 1
    while $attempt <= $retries and $failures {
      notice("Retry attempt ${attempt}...")
      sleep($delay)
      $retry_results = run_task('complex_puppet_bolt_task::get_interface_facts', $failures.target_spec)
      $failures = $retry_results.error_set
      $attempt += 1
    }

    if $failures {
      fail("Task failed on the following targets even after ${retries} retries: ${failures.target_spec}")
    }
  }

  return $results
}
