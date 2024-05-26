plan complex_puppet_bolt_task::configure_routers (
  TargetSpec $targets
) {
  $results = run_task('complex_puppet_bolt_task::get_interface_facts', $targets)
  out::message("Results: ${results}")
  return $results
}
