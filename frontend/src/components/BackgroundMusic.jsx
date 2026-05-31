import { useEffect, useRef, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";
import song from "../assets/lagu.mp3";

export default function BackgroundMusic() {
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;

    async function playMusic() {
      const mutedByUser = localStorage.getItem("wariga-music-muted") === "true";

      if (mutedByUser || !audio.paused) {
        return;
      }

      try {
        await audio.play();
        setPlaying(true);
      } catch {
        setPlaying(false);
      }
    }

    function syncPlayingState() {
      setPlaying(!audio.paused);
    }

    function playAfterInteraction(event) {
      if (
        event.target instanceof Element &&
        event.target.closest("[data-music-toggle]")
      ) {
        return;
      }

      playMusic();
    }

    playMusic();
    audio.addEventListener("play", syncPlayingState);
    audio.addEventListener("pause", syncPlayingState);
    document.addEventListener("pointerdown", playAfterInteraction);
    document.addEventListener("keydown", playAfterInteraction);

    return () => {
      audio.removeEventListener("play", syncPlayingState);
      audio.removeEventListener("pause", syncPlayingState);
      document.removeEventListener("pointerdown", playAfterInteraction);
      document.removeEventListener("keydown", playAfterInteraction);
    };
  }, []);

  async function toggleMusic() {
    const audio = audioRef.current;

    if (audio.paused) {
      try {
        localStorage.removeItem("wariga-music-muted");
        await audio.play();
        setPlaying(true);
      } catch {
        setPlaying(false);
      }
      return;
    }

    audio.pause();
    localStorage.setItem("wariga-music-muted", "true");
    setPlaying(false);
  }

  return (
    <>
      <audio ref={audioRef} src={song} autoPlay loop preload="auto" />
      <button
        className="fixed bottom-5 right-5 z-50 flex items-center justify-center gap-2 rounded-full bg-baliBrown px-4 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-[#442313]"
        type="button"
        data-music-toggle
        onClick={toggleMusic}
        aria-label={playing ? "Matikan musik" : "Putar musik"}
        title={playing ? "Matikan musik" : "Putar musik"}
      >
        {playing ? <Volume2 size={19} /> : <VolumeX size={19} />}
        <span>{playing ? "Musik Aktif" : "Putar Musik"}</span>
      </button>
    </>
  );
}
