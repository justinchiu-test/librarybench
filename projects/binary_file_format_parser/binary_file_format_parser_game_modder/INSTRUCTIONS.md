# PyBinParser - Game Save File Modification Tool

## Overview
A binary parser specifically designed for game modding enthusiasts who need to understand and modify proprietary save game formats. This tool enables reverse engineering of undocumented save file structures, pattern recognition across multiple saves, and safe modification of game data.

## Persona Description
An enthusiastic gamer who creates tools and mods by editing save game files for various titles. They need to understand proprietary formats without official documentation and share their findings with the modding community.

## Key Requirements
1. **Format Learning Mode**: Automatically infer binary structure by analyzing multiple save file samples from the same game, identifying common patterns, field boundaries, and data types through comparative analysis. This enables modders to decode formats without documentation.

2. **Visual Diff Highlighting**: Compare save files before and after specific game actions to identify which binary regions changed, helping modders understand how game state maps to file structure. Must support side-by-side comparison with color-coded differences.

3. **Type Inference System**: Automatically detect and classify data types (integers, floats, strings, arrays) within binary data by analyzing value patterns and ranges. Should recognize common game data like coordinates, health values, and inventory counts.

4. **Community Schema Sharing**: Export and import format definitions in a standardized schema language that can be shared with other modders. Includes versioning support for different game patches and collaborative format documentation.

5. **Safe Value Boundary Detection**: Analyze value ranges across multiple save files to determine safe modification limits, preventing save corruption from out-of-bounds values. Must warn when proposed changes exceed observed boundaries.

## Technical Requirements
- **Testability**: All analysis, inference, and modification functions must be fully testable via pytest
- **Performance**: Process save files up to 50MB with real-time diff analysis
- **Data Safety**: Never modify original files; always work on copies with validation
- **Format Flexibility**: Support both fixed-structure and variable-length save formats
- **No UI Components**: Command-line and programmatic API only

## Core Functionality
The parser must provide:
- Multi-file analysis for structure inference
- Binary diff engine with change tracking
- Statistical type inference based on value patterns
- Schema definition language for format documentation
- Import/export of community-shared schemas
- Boundary analysis and validation system
- Safe modification API with rollback support
- Checksum calculation and repair utilities

## Testing Requirements
Comprehensive test coverage must include:
- **Format Learning**: Test structure inference with synthetic save file sets
- **Diff Analysis**: Verify accurate change detection between file versions
- **Type Inference**: Validate correct type identification for known data patterns
- **Schema Operations**: Test import/export of format definitions
- **Boundary Detection**: Verify safe limit calculations from sample data
- **Modification Safety**: Ensure changes don't corrupt file structure
- **Performance Tests**: Confirm real-time analysis for large files
- **Edge Cases**: Handle compressed saves, encrypted sections, nested structures

All tests must be executable via:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria
The implementation is successful when:
- All pytest tests pass with 100% success rate
- A valid pytest_results.json file is generated showing all tests passing
- Format learning correctly infers structure from multiple file samples
- Diff highlighting accurately identifies all changed regions
- Type inference achieves 90%+ accuracy on common game data types
- Schema sharing produces valid, importable format definitions
- Boundary detection prevents all unsafe modifications in test cases
- Performance meets real-time requirements for 50MB files
- Modified saves remain loadable in their respective games (simulated in tests)

## Environment Setup
To set up the development environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```