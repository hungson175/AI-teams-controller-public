/**
 * Hand-Free JS Talk - Backend Server
 *
 * Provides:
 * 1. Ephemeral token generation for OpenAI Realtime API
 * 2. File saving endpoint for transcriptions
 * 3. Static file serving for frontend
 */

import express from 'express';
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
app.use(express.json());
app.use(express.static(__dirname));

const PORT = process.env.PORT || 3456;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TRANSCRIPTS_DIR = join(__dirname, 'transcripts');

// Ensure transcripts directory exists
if (!existsSync(TRANSCRIPTS_DIR)) {
  await mkdir(TRANSCRIPTS_DIR, { recursive: true });
}

/**
 * GET /api/token
 * Generate ephemeral token for OpenAI Realtime API
 */
app.get('/api/token', async (req, res) => {
  if (!OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not configured' });
  }

  try {
    const response = await fetch('https://api.openai.com/v1/realtime/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-realtime-preview-2024-12-17'
      })
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('OpenAI API error:', error);
      return res.status(response.status).json({ error: 'Failed to get token' });
    }

    const data = await response.json();
    res.json({
      token: data.client_secret.value,
      expires_at: data.client_secret.expires_at
    });
  } catch (error) {
    console.error('Token generation error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/save-transcript
 * Save transcription to file with timestamp
 */
app.post('/api/save-transcript', async (req, res) => {
  const { text } = req.body;

  if (!text || text.trim() === '') {
    return res.status(400).json({ error: 'No text provided' });
  }

  // Generate filename with datetime to the second
  const now = new Date();
  const timestamp = now.toISOString()
    .replace(/[-:]/g, '')
    .replace('T', '_')
    .replace(/\.\d{3}Z$/, '');

  const filename = `${timestamp}_voice.txt`;
  const filepath = join(TRANSCRIPTS_DIR, filename);

  try {
    await writeFile(filepath, text.trim(), 'utf-8');
    console.log(`Saved transcript: ${filename}`);
    res.json({ success: true, filename });
  } catch (error) {
    console.error('Save error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/transcripts
 * List all saved transcripts
 */
app.get('/api/transcripts', async (req, res) => {
  const { readdir, readFile } = await import('fs/promises');

  try {
    const files = await readdir(TRANSCRIPTS_DIR);
    const transcripts = await Promise.all(
      files
        .filter(f => f.endsWith('_voice.txt'))
        .sort()
        .reverse()
        .slice(0, 20)
        .map(async (filename) => {
          const content = await readFile(join(TRANSCRIPTS_DIR, filename), 'utf-8');
          return { filename, content };
        })
    );
    res.json(transcripts);
  } catch (error) {
    res.json([]);
  }
});

app.listen(PORT, () => {
  console.log(`Hand-Free JS Talk server running at http://localhost:${PORT}`);
  console.log(`Transcripts will be saved to: ${TRANSCRIPTS_DIR}`);
  if (!OPENAI_API_KEY) {
    console.warn('WARNING: OPENAI_API_KEY not set!');
  }
});
