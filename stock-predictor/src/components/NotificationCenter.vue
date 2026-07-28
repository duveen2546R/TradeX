<template>
  <div class="fixed top-5 right-5 z-50 flex flex-col gap-3 w-80 max-w-[calc(100vw-2.5rem)] pointer-events-none" aria-live="polite">
    <TransitionGroup name="toast">
      <article
        v-for="(item, index) in visible"
        :key="item.id || index"
        class="toast-card pointer-events-auto bg-white dark:bg-[#0a0a0a] rounded-xl shadow-lg dark:shadow-none border border-gray-100 dark:border-[#1a1a1a] p-4 transition-all duration-300"
      >
        <strong v-if="item.title" class="block font-bold text-black dark:text-white text-sm tracking-tight leading-snug mb-1">
          {{ item.title }}
        </strong>
        <span v-if="item.body || item.message || item.text" class="block text-gray-600 dark:text-gray-400 text-sm leading-relaxed font-normal">
          {{ item.body || item.message || item.text }}
        </span>
      </article>
    </TransitionGroup>
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
  window.addEventListener("pointerdown", () => { audioEnabled = true; audioContext = new AudioContext(); }, { once: true });
  try {
    const { data } = await api.get("/api/notifications");
    visible.value = data.slice(0, 2);
  } catch (_) {}
  source = new EventSource(`${api.defaults.baseURL}/api/stream/notifications`, { withCredentials: true });
  source.onmessage = (event) => notify(JSON.parse(event.data));
});
onUnmounted(() => source?.close());
</script>

<style scoped>
.toast-card {
  border-left: 4px solid #10b981;
}

.toast-enter-active,
.toast-leave-active,
.toast-move {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
