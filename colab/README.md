# Colab Modules

The supplied local Colab Python exports are:

- `C:/Users/a0983/Downloads/即時戰情室.py`
- `C:/Users/a0983/Downloads/智能判讀指數.py`
- `C:/Users/a0983/Downloads/智能選股.py`
- `C:/Users/a0983/Downloads/自動化戰情模組.py`

They were inspected locally and contain useful LionKing strategy logic, but some exports also contain hard-coded API tokens or broker/API key placeholders. Because this repository is public, upload the sanitized versions only.

Recommended target paths:

- `colab/即時戰情室.py`
- `colab/智能判讀指數.py`
- `colab/智能選股.py`
- `colab/自動化戰情模組.py`

Before upload, replace any hard-coded token/key with environment variables, for example:

```python
import os
FINMIND_TOKEN = os.environ.get("FINMIND_TOKEN")
SHIOAJI_API_KEY = os.environ.get("SHIOAJI_API_KEY")
SHIOAJI_SECRET_KEY = os.environ.get("SHIOAJI_SECRET_KEY")
```

The Supabase metadata rows for these modules are defined in `supabase/schema_lion_king_v110.sql`.
