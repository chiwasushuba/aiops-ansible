# aiops-ansible project guidance

## Purpose and current state

This repository is intended for Ansible-based DevOps automation, CI/CD, and
AWS architecture with an emphasis on EC2 and free-first implementations.
Ansible now prepares an existing Ubuntu 24.04 amd64 host and deploys the sibling
aiops backend, PostgreSQL 17 and Caddy with Compose. React/Vite stays on Vercel.
There are no AWS provisioning or CI workflows. Supported control nodes are Linux
or WSL with Python 3.12; inspect README and pinned requirements before execution.

## Change workflow

- Read the applicable global instructions, inspect Git state and relevant
  files, and state the intended changes before substantive edits.
- Preserve existing work. Implement only the requested infrastructure,
  automation, or delivery scope, then run proportionate checks and report them.
- Prefer local rehearsal, existing hardware, and community tooling. For AWS,
  verify account plan/eligibility, region, workload, credits and expiry before
  describing an implementation as free. Include recurring cost after credits.
- Default to a small EC2 design with systemd or Compose only when it satisfies
  the workload. Explain any need for managed NAT, load balancing, multi-AZ,
  managed databases, Kubernetes, or a persistent CI controller and its cost.
- Design and repository edits do not authorize provisioning, deployments, live
  Ansible runs, IAM/billing changes, resource deletion, or buying commitments.
  Reuse concrete authorization already supplied for those actions.

## Capability routing

Reuse the installed global capabilities rather than duplicating their prompts:

| Work | Agent | Skills |
| --- | --- | --- |
| Ansible and declarative infrastructure | `iac-engineer` | `$infrastructure-as-code` |
| CI/CD jobs, runner trust, release artifacts | `pipeline-architect` | `$pipeline-architecture` |
| EC2 topology, sizing, access, storage, recovery | `cloud-architect` | `$aws-ec2-architecture` |
| Containers, reverse proxy, host/runtime delivery | `platform-engineer` | `$delivery-platform`, `$systems-operations` |
| Cost, allowance, expiry, retained-resource review | `cloud-cost-reviewer` | `$free-first-operations` |

For new labs and budget-sensitive changes, compose `$free-first-operations`
with the owning skill. Use agents only when delegation benefits the task and
is authorized; ordinary scoped work can stay with the primary agent.

## Ansible and EC2 conventions

- When adding automation, separate nonsecret inventories and environment
  variables from reusable roles/playbooks. Pin required collections and document
  the supported control-node environment. Use Linux or WSL for Ansible execution
  unless the selected toolchain explicitly supports another environment.
- Prefer idempotent modules, explicit privilege escalation, scoped host groups,
  handlers, and serialized/batched disruptive changes. Review `delegate_to`,
  local actions, inventory plugins, and tasks that call AWS APIs for side effects.
- Keep passwords, private keys, cloud credentials, decrypted Vault data, state,
  sensitive plans, and session output out of Git and reports. Never embed secrets
  in user data. Use instance roles and short-lived CI identity where supported.
- Restrict SSH/SSM and database access. Check SSM agent, IAM and outbound-network
  prerequisites; include public-address/NAT/endpoint costs in the design.
- Keep untrusted CI execution away from deployment credentials and the application
  host. Build/test locally or on an appropriate isolated runner, then deploy the
  immutable artifact only through the authorized release path.
- Make persistent data, backups, restore, health checks, rollback, log retention,
  expiry, and cleanup ownership explicit. Stopping an instance is not evidence
  that all AWS costs have stopped.

## Verification

Offline checks from repository root, after installing requirements:
`ansible-playbook -i inventories/production/hosts.example.yml playbooks/site.yml --syntax-check`,
`ansible-lint`, and `python scripts/validate_templates.py`. Set ANSIBLE_CONFIG
explicitly for a world-writable WSL-mounted checkout. These do not prove live
deployment, capacity, application integration or database restoration. See README
for setup, live playbooks and their authorization boundary.

- Ansible: begin with offline syntax/lint and inventory review using nonsecret
  test inputs. Inventory loading can execute plugins; inspect them first. Use an
  isolated test target for check mode and idempotence only within authorization.
  Check mode and diff are not universal safety guarantees or secret redaction.
- IaC: format and offline validation precede any authorized provider-backed plan.
  Inspect replacements, deletion, IAM, network paths, storage and recurring cost.
- CI/runtime: validate workflow/configuration and artifact handoff locally where
  possible. Distinguish those results from deployments and service health.
- Codex guidance: parse `.codex/config.toml`; check skill registration if local
  skills are introduced, and verify the managed overlay matches this project.

## Project Codex extensions and feedback

Keep project agents, skills, and their registrations under `.codex/`. Add a
project skill or agent only after a recurring repository-specific workflow or
distinct role is established. Register each project skill in `.codex/config.toml`
with an enabled `[[skills.config]]` entry. Broad engineering methods remain in
the reusable global environment.

The managed overlay lives at `codex-environment/projects/aiops-ansible/`.
Keep it aligned using the environment's guarded project sync workflow. Keep
project lessons here; promote reusable lessons globally only when that
maintenance is explicitly requested.
