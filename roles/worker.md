# Role: Worker

> Rule: If skillary.lock exists in project root or ~/.claude/, restrict skill selection to locked slugs and print using skillary.lock (N skills).

capabilities: read.file, write.file, edit.file, exec.shell
workspace: branch
deliverable: assigned-deliverable.md
mounts: assigned by planner
never: dispatches, touches the root working tree, deploys

## Job
Execute the assigned stage according to the deliverable contract and mounted skill instructions.
