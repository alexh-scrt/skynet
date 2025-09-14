# Import Issues Resolution

## Problem
Test files cannot import modules from the `src/` directory due to Python path issues.

## Solution
Use this pattern in all test files and standalone scripts:

```python
import sys
from pathlib import Path

# Add project root to path (not src directly)
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

# Now import from src
from src.utils.conversation_logger import BarbieConversationManager
from src.utils.agreement_detector import AgreementDetector
```

## Key Points

1. **Use `Path(__file__).parent.parent`** to get project root
2. **Add project root to sys.path**, not src directory
3. **Keep `src.` prefix** in import statements
4. **Place this code before any src imports**

## File Locations

### For files in `/tests/` directory:
```python
prj_root = Path(__file__).parent.parent  # Goes up to project root
```

### For files in project root:
```python
prj_root = Path(__file__).parent  # Already at project root
```

## Example Locations

```
/home/ubuntu/skynet/               <- project root
├── src/
│   ├── utils/
│   │   ├── conversation_logger.py
│   │   └── agreement_detector.py
│   └── ...
├── tests/                         <- test files here
│   ├── test_conversation_logging.py
│   └── ...
├── barbie.py                      <- main files here
├── ken.py
└── demo_*.py                      <- demo files here
```

## Working Examples

### In `/tests/test_conversation_logging.py`:
```python
import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import BarbieConversationManager
```

### In `/demo_agreement_detection_fix.py`:
```python
import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent
sys.path.insert(0, str(prj_root))

from src.utils.agreement_detector import AgreementDetector
```

## What NOT to do

❌ **Don't add src directory:**
```python
src_path = Path(__file__).parent.parent / "src"  # Wrong!
sys.path.insert(0, str(src_path))
```

❌ **Don't remove src prefix:**
```python
from utils.conversation_logger import BarbieConversationManager  # Wrong!
```

## Integration with barbie.py

The main `barbie.py` file uses this pattern:
```python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.conversation_logger import BarbieConversationManager
from src.utils.agreement_detector import AgreementDetector
```

This works because `barbie.py` is in the project root, so it adds the project root to the path, allowing imports with the `src.` prefix.