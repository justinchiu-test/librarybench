# The Task

I am a Security Specialist building a secrets provisioning CLI for infrastructure automation. I want a hardened interactive form to collect vault paths, roles, and access policies, then verify and review everything before writing to the secure backend. This code repository gives me a battle-tested, extensible CLI form framework.

# The Requirements

* `ask_text` : Secure single-line inputs for vault paths, policy names, or regex-validated tag keys, with length limits and placeholder hints.
* `branch_flow` : Conditional branching for different secret engines (KV, PKI, SSH), dynamically showing relevant fields in the correct order.
* `load_choices_async` : On-demand retrieval of existing secret paths, role lists, or certificate authorities from the Vault API, complete with spinners and cache.
* `input_line_fallback` : A fallback text-only prompt mode so the tool works even in minimal containers or remote agents without advanced terminals.
* `review_submission` : A final review screen summarizing policies, ACLs, and metadata, all editable before committing secrets.
* `ask_password` : Obscured entry for master keys or root tokens, with optional strength meter and toggle to unmask for verification.
* `select_choices` : Arrow-key navigable lists for selecting multiple policies, roles, or approvers in one step.
* `set_renderer_theme` : Support for high-contrast or dark-mode themes to meet accessibility and security-ops console standards.
* `register_on_change` : Callback hooks to enforce policy naming conventions or to auto-populate default TTLs when roles change.
* `format_errors` : Customizable global and per-field error templates for vault path collisions, invalid ACL syntax, or missing entitlements, with colorized inline hints.
