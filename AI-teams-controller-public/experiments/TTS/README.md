# TTS API Alternatives - Cheaper & Better Than OpenAI

**Research Date**: 2025-12-16
**Full Research**: See `TTS-RESEARCH.md`

## Quick Summary

OpenAI TTS costs **$15/million characters** and is relatively slow. Here are better alternatives:

## Top 3 Recommendations

### 1. 🏆 Google Cloud Standard - BEST VALUE
- **Cost**: $4/million (73% cheaper than OpenAI)
- **Free tier**: 4M chars/month
- **Quality**: Decent (acceptable for notifications/feedback)
- **Speed**: ~200ms
- **Setup**: Medium (requires Google Cloud account)

👉 **Demo**: `google-cloud/`

---

### 2. ⚡ Deepgram Aura-2 - BEST SPEED
- **Cost**: $15/million (same as OpenAI)
- **Speed**: 250-300ms (2-5x faster overall)
- **Quality**: Excellent (beats ElevenLabs and OpenAI)
- **Setup**: Easy (simple API key)

👉 **Demo**: `deepgram/`

---

### 3. 💰 Piper TTS - FREE & OPEN-SOURCE
- **Cost**: $0 (completely free)
- **Speed**: Fast (runs locally on CPU)
- **Quality**: Decent (good for testing)
- **Setup**: Easy (pip install)

👉 **Demo**: `piper-tts/`

---

## Cost Comparison Table

| Provider | 1M chars | 10M chars | vs OpenAI | Speed |
|----------|----------|-----------|-----------|-------|
| **Piper (free)** | $0 | $0 | 100% cheaper | Fast |
| **Google Standard** | $4 | $40 | 73% cheaper | 200ms |
| **Murf.ai** | $10 | $100 | 33% cheaper | <55ms |
| **OpenAI** | $15 | $150 | Baseline | 200ms |
| **Deepgram** | $15 | $150 | Same | 250-300ms* |
| **Google Neural2** | $16 | $160 | 7% more | 200ms |
| **Azure** | $16 | $160 | 7% more | 150ms |
| **ElevenLabs** | $165 | $1,650 | 1,000% more | 75ms |

*Deepgram is faster overall (2-5x) despite higher TTFB due to streaming optimizations

---

## Which Should You Use?

### For Your AI Teams Controller Project

**Current state**: Using OpenAI at $15/million which is "expensive and slow"

**Recommendation (3-phase approach):**

#### Phase 1 (This Week): Test Google Cloud Standard
```bash
cd google-cloud/
python demo.py
```

- 73% cost reduction ($4 vs $15)
- Use 4M free chars/month to test
- If quality acceptable → migrate immediately

#### Phase 2 (Optional): Test Deepgram for Speed
```bash
cd deepgram/
python demo.py
```

- Same cost as OpenAI but 2-5x faster
- Better for real-time voice feedback
- Test if speed improvement is noticeable

#### Phase 3 (Experiment): Try Piper TTS
```bash
cd piper-tts/
python demo.py
```

- Zero cost for testing/development
- Good for understanding actual usage volume
- Can run offline

---

## Setup & Testing

### 1. Google Cloud TTS (Recommended)

```bash
cd experiments/TTS/google-cloud
pip install google-cloud-texttospeech

# Set up credentials (see README.md)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Run demo
python demo.py
```

**Generates**:
- `output_google_standard.mp3` - Cheap voice ($4/million)
- `output_google_neural2.mp3` - Premium voice ($16/million)
- `output_google_vietnamese.mp3` - Vietnamese test

### 2. Deepgram Aura (Fast)

```bash
cd experiments/TTS/deepgram
pip install deepgram-sdk

# Set API key
export DEEPGRAM_API_KEY="your_key_here"

# Run demo
python demo.py
```

**Generates**: `output_deepgram.mp3`

### 3. Piper TTS (Free)

```bash
cd experiments/TTS/piper-tts
pip install piper-tts

# No API key needed!
python demo.py
```

**Generates**: `output_piper.wav`

---

## Vietnamese Support

All three demos support Vietnamese:

- ✅ **Google Cloud**: Full Vietnamese support (Standard + Neural2)
- ✅ **Deepgram**: Check model availability
- ✅ **Piper**: Check [voice models list](https://github.com/rhasspy/piper/blob/master/VOICES.md)

---

## Decision Tree

```
Do you need premium quality?
├─ YES → Consider ElevenLabs ($165/M) or Azure ($16/M with 5M free)
└─ NO → Continue...

Is speed critical (real-time voice apps)?
├─ YES → Use Deepgram ($15/M, 2-5x faster)
└─ NO → Continue...

Want maximum cost savings?
├─ YES → Use Google Standard ($4/M, 73% cheaper)
└─ NO → Continue...

Want to experiment for free?
├─ YES → Use Piper TTS ($0, open-source)
└─ NO → Stick with OpenAI
```

---

## Quick Action Plan

**For immediate savings (this week):**

1. **Test Google Cloud Standard**
   ```bash
   cd google-cloud && python demo.py
   ```

2. **Compare audio quality** with current OpenAI output

3. **If acceptable** → migrate and save 73%

4. **If not acceptable** → try Google Neural2 (7% more than OpenAI but better free tier)

---

## Full Research Report

See **`TTS-RESEARCH.md`** for:
- Detailed provider comparison
- Open-source alternatives (XTTS-v2, Bark, etc.)
- Speed benchmarks
- Vietnamese language support
- Self-hosting cost analysis
- Complete source citations

---

## Questions?

- Check individual demo READMEs for detailed setup
- Run demos to hear actual voice quality
- Read `TTS-RESEARCH.md` for comprehensive analysis

**Bottom line**: OpenAI TTS is overpriced. Google Cloud Standard saves you 73% with acceptable quality.
