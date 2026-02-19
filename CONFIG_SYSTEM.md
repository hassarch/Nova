# NOVA Configuration System

## Overview

NOVA now has a professional, user-configurable system that transforms it from a hardcoded runtime into a flexible tool.

## Architecture

### Three-Layer Design

1. **Schema Layer** (`nova/config/schema.py`)
   - Pydantic model with type validation
   - Sensible defaults
   - Future-proof extensibility

2. **Loader Layer** (`nova/config/loader.py`)
   - Handles file I/O
   - Graceful fallbacks
   - Always returns structured object

3. **CLI Layer** (`nova/main.py`)
   - `nova init` command
   - Config loaded on startup
   - Available globally as `config`

## Configuration File

### Location
```
~/.nova/config.yaml
```

### Default Content
```yaml
model: llama3
strict_git: true
max_retries: 3
sandbox_mode: false
default_simulation: false
max_execution_time: 60
protected_branches:
  - main
  - master
log_level: info
```

## Usage

### Initialize Configuration
```bash
nova init
```

Creates `~/.nova/config.yaml` with defaults.

### View Configuration
```bash
cat ~/.nova/config.yaml
```

### Modify Configuration
Edit `~/.nova/config.yaml` directly:
```yaml
model: llama2              # Change LLM model
max_retries: 5             # Increase retries
sandbox_mode: true         # Enable Docker sandbox
log_level: debug           # Enable debug logging
```

### Load Configuration in Code
```python
from nova.config.loader import load_config

config = load_config()
print(config.model)           # "llama3"
print(config.max_retries)     # 3
print(config.protected_branches)  # ["main", "master"]
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | str | `llama3` | LLM model to use |
| `strict_git` | bool | `true` | Enforce git safety checks |
| `max_retries` | int | `3` | Maximum retry attempts |
| `sandbox_mode` | bool | `false` | Run commands in Docker sandbox |
| `default_simulation` | bool | `false` | Default to simulation mode |
| `max_execution_time` | int | `60` | Max execution time in seconds |
| `protected_branches` | list | `["main", "master"]` | Branches protected from modifications |
| `log_level` | str | `info` | Logging level (debug, info, warning, error) |

## Implementation Details

### Pydantic Schema
- Type validation
- Default values
- Field descriptions
- Extra fields allowed for future extensibility

### Loader Behavior
1. If config file doesn't exist → return defaults
2. If exists → load and validate
3. If invalid → return defaults
4. Always returns `NovaConfig` object

### Global Access
Config is loaded on startup:
```python
# In nova/main.py
config = load_config()
```

Available throughout the application.

## Future Integration

The config system is designed to inject into:

- **Policy Engine** - Risk thresholds, protected branches
- **Recovery Engine** - Retry limits, git safety checks
- **Planner** - Model selection, execution time limits
- **Executor** - Sandbox mode, timeout settings

## Design Philosophy

✓ **One config model** - Pydantic BaseModel  
✓ **One config loader** - Centralized loading logic  
✓ **One global accessor** - Loaded on startup  
✓ **Zero scattered config reads** - No hardcoded values  
✓ **Professional structure** - Like mature open-source tools  

## Testing

Config system is tested and verified:
- ✓ File creation works
- ✓ YAML parsing works
- ✓ Defaults applied correctly
- ✓ Type validation works
- ✓ All CI checks pass

## Next Steps

1. Inject config into PolicyEngine
2. Inject config into RecoveryEngine
3. Inject config into Planner
4. Add config validation command
5. Add config reset command
