# LionKing Reference Assets

These are the local reference assets supplied on 2026-04-29. The current Codex GitHub connector can create/update UTF-8 text files, but it cannot directly stream local PDF/JPG binaries from `C:/Users/a0983/Downloads` into GitHub.

## PDF references

| Target repo path | Local source | Size |
| --- | --- | ---: |
| `references/股票策略分析參考圖.pdf` | `C:/Users/a0983/Downloads/股票策略分析參考圖.pdf` | 4,889,758 bytes |
| `references/即時戰情室 - Colab.pdf` | `C:/Users/a0983/Downloads/即時戰情室 - Colab.pdf` | 1,136,868 bytes |
| `references/智能判讀指數 - Colab.pdf` | `C:/Users/a0983/Downloads/智能判讀指數 - Colab.pdf` | 719,746 bytes |
| `references/智能選股 - Colab.pdf` | `C:/Users/a0983/Downloads/智能選股 - Colab.pdf` | 3,461,521 bytes |
| `references/自動化戰情模組 - Colab.pdf` | `C:/Users/a0983/Downloads/自動化戰情模組 - Colab.pdf` | 2,391,805 bytes |

## Image references

| Target repo path | Local source | Size |
| --- | --- | ---: |
| `references/股票分析建議參考圖(1).JPG` | `C:/Users/a0983/Downloads/股票分析建議參考圖(1).JPG` | 526,895 bytes |
| `references/股票分析建議參考圖(2).JPG` | `C:/Users/a0983/Downloads/股票分析建議參考圖(2).JPG` | 251,547 bytes |
| `references/股票分析建議參考圖(3).JPG` | `C:/Users/a0983/Downloads/股票分析建議參考圖(3).JPG` | 415,920 bytes |
| `references/股票分析建議參考圖(4).jpg` | `C:/Users/a0983/Downloads/股票分析建議參考圖(4).jpg` | 368,379 bytes |

## Recommended upload methods

1. Install Git for Windows and GitHub CLI, then commit the `references/` files locally.
2. Or upload these files through the GitHub web UI into the paths listed above.
3. Or upload them to Supabase Storage bucket `lion-king-assets` and store public URLs in `public.lion_king_reference_assets`.

Do not commit API tokens or broker secrets inside Colab notebooks/scripts. Use GitHub Secrets and Supabase environment variables instead.
