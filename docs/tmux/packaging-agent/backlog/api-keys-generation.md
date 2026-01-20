# Generate Test API Keys for Public Distribution - CRITICAL

**Priority**: P0 - Required before ANY public distribution
**Time**: 30 minutes (key generation + file updates)
**Owner**: Boss (PO reminds Boss to do this)

---

## ⚠️ CRITICAL: PREPAID/SPENDING LIMITS REQUIRED

**Why critical**: Postpaid keys with public access = unlimited bill drain

**Action**: Verify each key has spending limits/prepaid balance BEFORE adding to repo

**Safety**: Set low spending caps ($5-10) on all test keys

---

## ⚠️ CRITICAL: KEY REVOCATION WARNING

**IMPORTANT**: These test API keys might be REMOVED/REVOKED at ANY time.

**Why**: Boss cannot sponsor every user forever. Prepaid limits will run out.

**MANDATORY for ALL scripts/docs using these keys**:

Add prominent warning:
```
⚠️ WARNING: The included test API keys may have been revoked already.
If you see authentication errors, you need to provide your own API keys.
These are temporary test keys for initial testing only.
```

**Files that MUST include this warning**:
- `install-web-ui.sh` - During installation
- `install-memory-system.sh` - During installation
- Backend README.md - In setup instructions
- Memory System INSTALLATION.md - In configuration section
- Main README.md - In Quick Start section

**When keys are revoked**: Users will see auth errors and MUST configure their own keys.

---

## Keys to Generate

Boss: Remind me to create these:

1. **XAI_API_KEY** - xAI API for Grok LLM
   - ⚠️ CHECK: PREPAID or spending limit

2. **SONIOX_API_KEY** - Soniox speech recognition
   - ⚠️ CHECK: PREPAID or spending limit

3. **VOYAGE_API_KEY** - Voyage AI embeddings (memory system)
   - ⚠️ CHECK: PREPAID or spending limit

4. **GOOGLE_APPLICATION_CREDENTIALS** - Google Cloud TTS service account JSON
   - ⚠️ CHECK: PREPAID or spending limit

5. **OPENAI_API_KEY** - OpenAI (for TTS option + experiments)
   - ⚠️ CHECK: PREPAID or spending limit

6. **HDTTS_API_KEY** - HD-TTS self-hosted (if applicable)
   - ⚠️ CHECK: PREPAID or spending limit

---

## Update Files with Test Keys

**Files to update** (NOT .gitignored - for testing):
- `AI-teams-controller-public/backend/.env`
- `memory-system/.env`

**Add comments with REVOCATION WARNING**:
```bash
# ⚠️ WARNING: This test API key may be REVOKED at any time.
# Boss cannot sponsor every user forever (prepaid limits run out).
# If you see auth errors, configure your own API key.
# TO-BE-REMOVED: Temporary test key for initial testing only.
XAI_API_KEY=your-test-key-here
```

**Format for ALL test keys**: Include revocation warning + TO-BE-REMOVED marker

---

## Provider Console Tracking

Boss: Add to-do in all provider consoles:

- **xAI Console**: "Delete TO-BE-REMOVED test key after public testing"
- **Soniox Console**: "Delete TO-BE-REMOVED test key after public testing"
- **Voyage AI Console**: "Delete TO-BE-REMOVED test key after public testing"
- **Google Cloud Console**: "Delete TO-BE-REMOVED service account after public testing"
- **OpenAI Console**: "Delete TO-BE-REMOVED test key after public testing"

---

## Why NOT Gitignored

**Reason**: Users can test immediately without configuring their own keys

**Security**: These are TEMPORARY test keys for public testing only

**Deletion timeline**: After public testing period, Boss deletes all test keys from provider consoles

---

## Checklist

- [ ] Generate NEW test API keys (all prefixed with "TO-BE-REMOVED-" in comments)
- [ ] Verify ALL keys are PREPAID or have low spending limits ($5-10)
- [ ] Update .env files with test keys
- [ ] Add REVOCATION WARNING + TO-BE-REMOVED comments to all keys in .env files
- [ ] Add revocation warnings to ALL installation scripts (install-web-ui.sh, install-memory-system.sh)
- [ ] Add revocation warnings to ALL documentation (Backend README, Memory INSTALLATION.md, main README)
- [ ] Add reminders in ALL provider consoles
- [ ] Commit keys to repo (intentional - not gitignored)
- [ ] Boss: Delete all test keys after public testing period
