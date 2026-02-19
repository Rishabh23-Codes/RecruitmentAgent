# 🎙️ RecruitmentAgent – Live Interview Frontend

This is the **React + Vite frontend** for the Live AI Interview module of RecruitmentAgent.

It connects to:
- 🎥 LiveKit (real-time audio/video)
- 🧠 Groq LLM (interview reasoning)
- 🗣️ Whisper STT
- 🔊 TTS voice synthesis
- 🤖 Bey AI Avatar
- 🐍 Flask backend (token + transcript relay)

---

## 🚀 Tech Stack

- React 18
- Vite
- LiveKit Client
- @livekit/components-react
- Tailwind / CSS
- pnpm / npm

---


### Configure Environment Variables
Create .env file:

```bash
VITE_LIVEKIT_URL="Same as the livekit_url". # must be string
# Example: "wss://your-project.livekit.cloud" 
```

