"""
AtlasTrinity TTS - Ukrainian Text-to-Speech

Uses robinhad/ukrainian-tts for agent voices:
- Atlas: Dmytro (male)
- Tetyana: Tetiana (female)
- Grisha: Mykyta (male)

NOTE: TTS models must be set up before first use via setup_dev.py
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import CONFIG_ROOT, MODELS_DIR
from ..config_loader import config

# Try to import ukrainian_tts properly
try:
    import ukrainian_tts

    # Lazy import to avoid loading Stanza at startup
    TTS_AVAILABLE = True
    print("[TTS] Ukrainian TTS available")
except ImportError:
    TTS_AVAILABLE = False
    print(
        "[TTS] Warning: ukrainian-tts not installed. Run: pip install git+https://github.com/robinhad/ukrainian-tts.git"
    )


@dataclass
class VoiceConfig:
    """Voice configuration for an agent"""

    name: str
    voice_id: str
    description: str


# Agent voice mappings
AGENT_VOICES = {
    "atlas": VoiceConfig(
        name="Atlas", voice_id="Dmytro", description="Male voice for Meta-Planner"
    ),
    "tetyana": VoiceConfig(
        name="Tetyana", voice_id="Tetiana", description="Female voice for Executor"
    ),
    "grisha": VoiceConfig(name="Grisha", voice_id="Mykyta", description="Male voice for Visor"),
}


class AgentVoice:
    """
    TTS wrapper for agent voices

    Usage:
        voice = AgentVoice("atlas")
        voice.speak("Hello, I am Atlas")
    """

    def __init__(self, agent_name: str, device: str = None):
        """
        Initialize voice for an agent

        Args:
            agent_name: One of 'atlas', 'tetyana', 'grisha'
            device: 'cpu', 'cuda', or 'mps' (Apple Silicon). If None, reads from config.yaml
        """
        self.agent_name = agent_name.lower()

        # Get device from config.yaml with fallback
        voice_config = config.get("voice.tts", {})
        self.device = device or voice_config.get("device", "mps")

        if self.agent_name not in AGENT_VOICES:
            raise ValueError(
                f"Unknown agent: {agent_name}. Must be one of: {list(AGENT_VOICES.keys())}"
            )

        self.config = AGENT_VOICES[self.agent_name]
        self._tts = None
        self._voice_enum = None  # Cache enum

        # Get voice enum
        if TTS_AVAILABLE:
            # Lazy import Voices as well
            try:
                from ukrainian_tts.tts import Voices

                self._voice_enum = getattr(Voices, self.config.voice_id, Voices.Dmytro)
                self._voice = self._voice_enum.value
            except Exception as e:
                print(f"[TTS] Failed to import Voices: {e}")
                # Set default voice
                self._voice = "Dmytro"
        else:
            self._voice = None

    @property
    def tts(self):
        """Lazy initialize TTS engine"""
        if self._tts is None and TTS_AVAILABLE:
            # Import only here to avoid issues during startup
            try:
                from ukrainian_tts.tts import TTS as UkrainianTTS

                global TTS
                TTS = UkrainianTTS
            except Exception as e:
                print(f"[TTS] Failed to import Ukrainian TTS: {e}")
                return None

            # Models should already be in MODELS_DIR from setup_dev.py
            if not MODELS_DIR.exists():
                print(f"[TTS] ⚠️  Models directory not found: {MODELS_DIR}")
                print("[TTS] Run setup_dev.py first to download TTS models")
                return None

            required_files = ["model.pth", "feats_stats.npz", "spk_xvector.ark"]
            missing = [f for f in required_files if not (MODELS_DIR / f).exists()]

            if missing:
                print(f"[TTS] ⚠️  Missing TTS model files: {missing}")
                print("[TTS] Run setup_dev.py to download them")
                return None

            try:
                print("[TTS] Initializing engine on " + str(self.device) + "...")
                print(
                    "downloading https://github.com/robinhad/ukrainian-tts/releases/download/v6.0.0"
                )
                self._tts = TTS(cache_folder=str(MODELS_DIR))
                print("downloaded.")
                print(f"[TTS] ✅ {self.config.name} voice ready on {self.device}")
            except Exception as e:
                print(f"[TTS] Error: {e}")
                import traceback

                traceback.print_exc()
                return None
        return self._tts

    def speak(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Generate speech from text

        Args:
            text: Ukrainian text to speak
            output_file: Optional path to save audio. If None, uses temp file

        Returns:
            Path to the generated audio file, or None if TTS not available
        """
        if not TTS_AVAILABLE:
            print(f"[TTS] [{self.config.name}]: {text}")
            return None

        if not text:
            return None

        # Determine output path
        if output_file is None:
            output_file = os.path.join(
                tempfile.gettempdir(), f"tts_{self.agent_name}_{hash(text) % 10000}.wav"
            )

        try:
            with open(output_file, mode="wb") as f:
                # Import Stress and Voices only here
                from ukrainian_tts.tts import Stress, Voices

                _, accented_text = self.tts.tts(
                    text, self._voice, Stress.Dictionary.value, f  # Use cached value
                )

            print(f"[TTS] [{self.config.name}]: {text}")
            return output_file

        except Exception as e:
            print(f"[TTS] Error generating speech: {e}")
            return None

    def speak_and_play(self, text: str) -> bool:
        """
        Generate speech and play it immediately (macOS)

        Args:
            text: Ukrainian text to speak

        Returns:
            True if successfully played, False otherwise
        """
        audio_file = self.speak(text)

        if audio_file and os.path.exists(audio_file):
            return self._play_audio(audio_file)

        return False

    def _play_audio(self, file_path: str) -> bool:
        """Play audio file on macOS"""
        try:
            import subprocess

            subprocess.run(["afplay", file_path], check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"[TTS] Error playing audio: {e}")
            return False


class VoiceManager:
    """
    Centralized TTS manager for all agents
    """

    def __init__(self, device: str = "cpu"):
        voice_config = config.get("voice.tts", {})
        self.enabled = voice_config.get("enabled", True)  # Check enabled flag
        self.device = device
        self._tts = None
        self.is_speaking = False  # Flag to prevent self-listening
        self.last_text = ""  # Last spoken text for echo filtering
        self.last_speak_time = 0.0  # End time of the last agent phrase

    @property
    def engine(self):
        if not self.enabled:
            print("[TTS] TTS is disabled in config")
            return None

        self._initialize_if_needed()
        return self._tts

    def _initialize_if_needed(self):
        if self._tts is None and TTS_AVAILABLE:
            print(f"[TTS] Initializing engine on {self.device}...")
            cache_dir = MODELS_DIR  # uses already imported MODELS_DIR
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Import TTS only here
            try:
                # IMPORTANT: ukrainian-tts (espnet2) expects to be in the model directory
                # to find feats_stats.npz and other files, even if cache_folder is passed.
                import os
                from contextlib import contextmanager

                from ukrainian_tts.tts import TTS as UkrainianTTS

                @contextmanager
                def tmp_cwd(path):
                    old_path = os.getcwd()
                    os.chdir(path)
                    try:
                        yield
                    finally:
                        os.chdir(old_path)

                with tmp_cwd(str(cache_dir)):
                    self._tts = UkrainianTTS(cache_folder=str(cache_dir), device=self.device)
            except Exception as e:
                print(f"[TTS] Failed to initialize engine: {e}")
                self._tts = None

    async def speak(self, agent_id: str, text: str) -> Optional[str]:
        """
        Generate and play speech for specific agent
        """
        if not TTS_AVAILABLE or not text:
            print(f"[TTS] [{agent_id.upper()}] (Text-only): {text}")
            return None

        agent_id = agent_id.lower()
        if agent_id not in AGENT_VOICES:
            print(f"[TTS] Unknown agent: {agent_id}")
            return None

        # Import Voices and Stress here
        from ukrainian_tts.tts import Stress, Voices

        config = AGENT_VOICES[agent_id]
        voice_enum = getattr(Voices, config.voice_id).value

        # Generate to temp file
        output_file = os.path.join(
            tempfile.gettempdir(), f"tts_{agent_id}_{hash(text) % 10000}.wav"
        )

        try:
            # Generate (CPU intensive, run in thread to avoid blocking loop)
            import asyncio

            def _generate():
                with open(output_file, mode="wb") as f:
                    self.engine.tts(text, voice_enum, Stress.Dictionary.value, f)

            await asyncio.to_thread(_generate)

            print(f"[TTS] [{config.name}]: {text}")
            self.last_text = text.strip().lower()

            # Play sequentially (await completion)
            self.is_speaking = True
            try:
                proc = await asyncio.create_subprocess_exec(
                    "afplay",
                    output_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode != 0:
                    print(f"[TTS] Playback error (afplay): {stderr.decode().strip()}")

                # Add a small grace period to prevent STT from catching the "tail" of echo
                await asyncio.sleep(0.5)
            finally:
                self.is_speaking = False
                import time

                self.last_speak_time = time.time()

            return output_file

        except Exception as e:
            print(f"[TTS] Error: {e}")
            return None
