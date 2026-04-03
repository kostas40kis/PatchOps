# Onboarding bootstrap - Demo Roundtrip Current\n\n## 1. Identity\n- **Project name:** Demo Roundtrip Current\n- **Target root:** `C:\dev\patchops\data\runtime\manual_repairs\patch_129_new_target_onboarding_flow_proof_20260328_183629\demo_roundtrip_current_target`\n- **Profile:** `generic_python`\n- **Wrapper root:** `C:\dev\patchops`\n- **Runtime path:** `(default profile runtime)`\n- **Project packet:** `C:\dev\patchops\docs\projects\demo_roundtrip_current.md`\n- **Current stage:** Initial onboarding\n\n## 2. Suggested reading order\n1. README.md\n2. docs/llm_usage.md\n3. docs/project_packet_contract.md\n4. docs/project_packet_workflow.md\n5. docs/projects/demo_roundtrip_current.md\n\n## 3. Initial goals\n- Create the current project packet\n- Generate the safest starter manifest\n\n## 4. Recommended command order\n1. check\n2. inspect\n3. plan\n4. apply or verify-only\n\n## 5. Notes\n- Keep PowerShell thin and let Python own reusable wrapper logic.\n- Treat the project packet as target-level memory and handoff as run-level resume state.\n\n<!-- PATCHOPS_CONTENT_PATH_ONBOARDING:START -->
## content_path onboarding note

### Maintained authoring rule
- author relative `content_path` values as wrapper-relative paths from the wrapper project root
- treat manifest-local resolution as compatibility fallback, not the primary contract
- prefer the maintained example manifest when introducing external content payloads for a new target

### Why new-target onboarding should care
- this avoids reintroducing the duplicated nested patch-prefix bug during first-time target authoring
- it keeps onboarding guidance aligned with the current runtime behavior, docs, handoff, and tests
- it keeps future LLMs from treating old manifest-local behavior as the preferred authoring rule
<!-- PATCHOPS_CONTENT_PATH_ONBOARDING:END -->\n