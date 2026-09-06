# Assurance Levels

This repository uses qualitative implementation classes to prevent semantic support from being mistaken for hardware assurance.

| Class | Example enforcement | Rollback claim | Alternate-egress claim |
|---|---|---:|---:|
| `SOFTWARE_REFERENCE` | Python/SQLite/API sink | false | false |
| `SOFTWARE_GATEWAY` | hardened service gateway | deployment-dependent | generally false |
| `ATTESTED_TEE` | measured TEE/confidential VM | possible | partial/deployment-dependent |
| `PROTECTED_FIRMWARE` | measured accelerator/device firmware + protected egress | possible | potentially strong |
| `SILICON_BACKED` | dedicated protected state + egress primitives | possible | potentially strongest |

These names are repository documentation conventions, not assigned IETF registry values.
