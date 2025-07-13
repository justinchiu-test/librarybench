# LibraryBench

Tools for synthesizing repositories that must be combined.

## Overview

LibraryBench provides a pipeline for:

1. Synthesizing tasks and variations
2. Generating tests for those tasks
3. Generating solutions for those tasks

## Generated Projects

All projects in this repository were generated using different Claude models. Below is a comprehensive table showing each project variant, the model used to generate it, and the lines of code (excluding tests).

### Project Statistics by Model

| Model | Number of Projects | Average Lines of Code |
|-------|-------------------|----------------------|
| Claude 4 Opus | 20 | 2,315 |
| Claude Sonnet 3.7 | 20 | 5,917 |
| **Total** | **40** | **4,116** |

### Complete Project List

| Project Name | Generating Model | Lines of Code |
|--------------|------------------|---------------|
| archive_file_manager_film | Claude 4 Opus | 1,757 |
| archive_file_manager_legal | Claude 4 Opus | 2,291 |
| binary_file_format_parser_audio_researcher | Claude 4 Opus | 2,369 |
| binary_file_format_parser_automotive_engineer | Claude 4 Opus | 1,620 |
| code_dependency_analyzer_legacy-modernizer | Claude 4 Opus | 1,979 |
| code_dependency_analyzer_performance-engineer | Claude 4 Opus | 1,337 |
| code_pattern_detector_performance_engineer | Claude 4 Opus | 2,395 |
| code_pattern_detector_security_auditor | Claude 4 Opus | 1,620 |
| command_line_task_manager_researcher | Claude Sonnet 3.7 | 12,710 |
| command_line_task_manager_security_analyst | Claude Sonnet 3.7 | 6,352 |
| concurrent_task_scheduler_render_farm_manager | Claude Sonnet 3.7 | 6,692 |
| concurrent_task_scheduler_scientific_computing | Claude Sonnet 3.7 | 14,208 |
| data_migration_framework_compliance_auditor | Claude 4 Opus | 4,242 |
| data_migration_framework_startup_cto | Claude 4 Opus | 5,806 |
| file_system_analyzer_db_admin | Claude Sonnet 3.7 | 5,501 |
| file_system_analyzer_security_auditor | Claude Sonnet 3.7 | 2,740 |
| http_api_mock_server_blockchain | Claude 4 Opus | 1,517 |
| http_api_mock_server_microservices | Claude 4 Opus | 1,671 |
| in_memory_database_ml_engineer | Claude Sonnet 3.7 | 4,760 |
| in_memory_database_mobile_developer | Claude Sonnet 3.7 | 4,465 |
| incremental_backup_system_digital_artist | Claude Sonnet 3.7 | 4,323 |
| incremental_backup_system_game_developer | Claude Sonnet 3.7 | 5,626 |
| memory_profiler_tool_embedded_engineer | Claude 4 Opus | 1,886 |
| memory_profiler_tool_game_developer | Claude 4 Opus | 1,661 |
| personal_finance_tracker_freelancer | Claude Sonnet 3.7 | 3,836 |
| personal_finance_tracker_socially_responsible_investor | Claude Sonnet 3.7 | 4,130 |
| personal_knowledge_management_academic_researcher | Claude Sonnet 3.7 | 5,831 |
| personal_knowledge_management_product_manager | Claude Sonnet 3.7 | 4,457 |
| process_resource_monitor_hft_developer | Claude 4 Opus | 557 |
| process_resource_monitor_k8s_engineer | Claude 4 Opus | 1,915 |
| query_language_interpreter_data_privacy_officer | Claude Sonnet 3.7 | 6,045 |
| query_language_interpreter_legal_discovery_specialist | Claude Sonnet 3.7 | 4,912 |
| template_rendering_engine_email_marketing | Claude 4 Opus | 1,824 |
| template_rendering_engine_report_generator | Claude 4 Opus | 2,259 |
| terminal_game_engine_ascii_art | Claude 4 Opus | 3,118 |
| terminal_game_engine_multiplayer | Claude 4 Opus | 4,304 |
| text_editor_student | Claude Sonnet 3.7 | 6,516 |
| text_editor_writer | Claude Sonnet 3.7 | 3,171 |
| virtual_machine_emulator_parallel_researcher | Claude Sonnet 3.7 | 12,064 |
| virtual_machine_emulator_security_researcher | Claude Sonnet 3.7 | 3,930 |

## Installation
1. Install claude code and codex

## Usage
```
bash scripts/synth_ideas.sh
bash scripts/synth_personas.sh
bash scripts/synth_instructions.sh
bash scripts/synth_code_tests.sh
```

## Environment Setup

LibraryBench requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (for OpenAI models)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude models)

