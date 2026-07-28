<template>
  <div class="notifications" aria-live="polite">
    <article v-for="item in visible" :key="item.id" class="toast">
      <strong>{{ item.title }}</strong><span>{{ item.body }}</span>
    </article>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import api from "../api";

const visible = ref([]);
let source;
let audioEnabled = false;
let audioContext;
function beep() {
  if (!audioEnabled || !audioContext) return;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.frequency.value = 880;
  gain.gain.setValueAtTime(0.06, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.18);
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start(); oscillator.stop(audioContext.currentTime + 0.18);
}
function notify(item) {
  visible.value.unshift(item);
  visible.value = visible.value.slice(0, 3);
  beep();
  window.setTimeout(() => { visible.value = visible.value.filter((current) => current !== item); }, 8000);
}
onMounted(async () => {
  // A user interaction is required before browsers permit audio playback.
  window.addEventListener("pointerdown", () => { audioEnabled = true; audioContext = new AudioContext(); }, { once: true });
  try {
    const { data } = await api.get("/api/notifications");
    visible.value = data.slice(0, 2);
  } catch (_) { /* Session may have expired; the router guard handles navigation. */ }
  source = new EventSource(`${api.defaults.baseURL}/api/stream/notifications`, { withCredentials: true });
  source.onmessage = (event) => notify(JSON.parse(event.data));
});
onUnmounted(() => source?.close());
</script>

<style scoped>
.notifications { position:fixed; z-index:50; right:22px; top:22px; display:grid; gap:12px; width:min(370px,calc(100vw - 44px)); }.toast { display:grid; gap:6px; padding:16px; border:1px solid rgba(45,212,191,.4); border-radius:18px; color:#ecfeff; background:linear-gradient(135deg,#12343be8,#0b1520e8); box-shadow:0 18px 42px #0009,inset 0 1px #ffffff12; backdrop-filter:blur(18px); animation:toast-in .35s ease-out; }.toast strong{color:#5eead4}.toast span { font-size:.9rem; line-height:1.45; color:#cbd5e1; }@keyframes toast-in{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
</style>
