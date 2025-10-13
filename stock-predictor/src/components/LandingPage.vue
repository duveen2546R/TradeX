<template>
  <div
    class="relative min-h-screen w-screen transition-all duration-700"
    :class="theme === 'dark' ? 'bg-[#050505] text-white' : 'bg-[#f6f9fb] text-gray-900'"
  >
    <!-- 🌫 Animated Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none z-0">
      <div class="fog"></div>
      <div class="light"></div>
      <div class="light-sweep"></div>
    </div>

    <!-- 🧭 Navbar -->
    <header
      class="flex justify-between items-center px-8 md:px-12 py-6 z-20 relative text-sm tracking-wide backdrop-blur-md bg-transparent"
    >
      <!-- App Name (No logo) -->
      <h1
        class="text-3xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-400 cursor-pointer"
        @click="$router.push('/')"
      >
        TradeX
      </h1>

      <div class="flex items-center gap-4 md:gap-6">
        <router-link
          to="/dashboard"
          class="hidden md:flex items-center gap-2 px-4 md:px-6 py-2 rounded-full text-sm font-semibold hover:bg-teal-600/20 border border-teal-400/30 transition-all duration-300"
        >
          <font-awesome-icon :icon="['fas', 'chart-line']" /> Dashboard
        </router-link>

        <!-- Theme Toggle -->
        <button
          @click="toggleTheme"
          class="border border-teal-400/30 px-3 md:px-4 py-2 rounded-full transition-all duration-300 text-sm"
          aria-label="Toggle Theme"
        >
          <font-awesome-icon :icon="['fas', theme === 'dark' ? 'sun' : 'moon']" />
          <span class="hidden md:inline ml-1">{{ theme === 'dark' ? 'Light' : 'Dark' }}</span>
        </button>
      </div>
    </header>

    <!-- ✨ Hero Section -->
    <main class="flex flex-col items-center justify-center text-center relative z-20 min-h-[85vh] px-6">
      <Motion :initial="{ opacity: 0, y: 40 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 1.2 }">
        <h1
          class="text-5xl md:text-7xl lg:text-[6rem] font-extrabold leading-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 via-cyan-300 to-white drop-shadow-2xl animate-glow"
        >
          Predict. Invest. Grow.
        </h1>
      </Motion>

      <Motion
        :initial="{ opacity: 0 }"
        :animate="{ opacity: 1 }"
        :transition="{ delay: 1.2, duration: 1.2 }"
        class="mt-10 flex flex-col sm:flex-row gap-4 sm:gap-6"
      >
        <router-link
          to="/dashboard"
          class="px-6 md:px-8 py-3 rounded-full text-base md:text-lg font-semibold bg-gradient-to-r from-teal-500 to-cyan-400 hover:scale-105 hover:shadow-xl transition-all duration-300"
        >
          <font-awesome-icon :icon="['fas', 'chart-area']" /> Launch Dashboard
        </router-link>

      </Motion>
    </main>

    <!-- 🌟 Features Section -->
    <section class="py-24 px-6 md:px-12 relative z-20">
      <!-- Parallax Fog -->
      <div class="absolute inset-0 opacity-20 pointer-events-none -z-10">
        <div class="parallax-fog"></div>
      </div>

      <div class="max-w-6xl mx-auto text-center relative z-10">
        <Motion
          :initial="{ opacity: 0, y: 30 }"
          :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.8 }"
        >
          <h2 class="text-4xl md:text-5xl font-bold mb-6">
            Why Choose <span class="text-teal-400">Eventra Stocks</span>?
          </h2>
          <p class="text-gray-500 dark:text-gray-400 max-w-2xl mx-auto text-base md:text-lg">
            Accelerate your investing journey with predictive insights, live analytics, and a seamless dashboard experience.
          </p>
        </Motion>

        <div class="features-grid grid md:grid-cols-3 gap-10 mt-16">
          <Motion
            v-for="(feature, i) in features"
            :key="i"
            :initial="{ opacity: 0, y: 60, scale: 0.9 }"
            :animate="{ opacity: 1, y: 0, scale: 1 }"
            :transition="{ delay: i * 0.3, duration: 0.8 }"
            class="feature-card"
          >
            <div class="icon">
              <font-awesome-icon :icon="feature.icon" />
            </div>
            <h4>{{ feature.title }}</h4>
            <p>{{ feature.text }}</p>
          </Motion>
        </div>
      </div>
    </section>

    <!-- 🦶 Footer -->
    <footer class="py-6 text-center text-gray-400 border-t border-teal-400/20 bg-transparent">
      © {{ new Date().getFullYear() }} Eventra Stocks — Predict. Analyze. Grow.
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Motion } from "@motionone/vue";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { fas } from "@fortawesome/free-solid-svg-icons";

library.add(fas);

const theme = ref(localStorage.getItem("theme") || "dark");

const applyTheme = () => {
  document.documentElement.classList.toggle("dark", theme.value === "dark");
  localStorage.setItem("theme", theme.value);
};
const toggleTheme = () => {
  theme.value = theme.value === "dark" ? "light" : "dark";
  applyTheme();
};
onMounted(applyTheme);

const features = [
  {
    icon: ["fas", "bolt"],
    title: "Real-Time Data",
    text: "Stream live market prices through Kafka — stay ahead of every trend.",
  },
  {
    icon: ["fas", "brain"],
    title: "AI Predictions",
    text: "Leverage machine learning to forecast market movements and build confidence.",
  },
  {
    icon: ["fas", "shield-alt"],
    title: "Secure & Scalable",
    text: "Powered by Flask, Kafka, and Vue for lightning-fast and reliable performance.",
  },
];
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap");

body {
  font-family: "Inter", sans-serif;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

/* 🌫 Background Animations */
.fog {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 60% 50%, rgba(255, 255, 255, 0.1), transparent 60%),
              radial-gradient(circle at 40% 50%, rgba(255, 255, 255, 0.05), transparent 50%);
  filter: blur(80px);
  animation: fogMove 20s ease-in-out infinite alternate;
  mix-blend-mode: screen;
}

.light {
  position: absolute;
  right: -10%;
  top: -10%;
  width: 80%;
  height: 120%;
  background: radial-gradient(circle at 60% 50%, rgba(255, 255, 255, 0.35), rgba(0, 200, 255, 0.15), transparent 80%);
  filter: blur(160px);
  animation: lightShift 18s ease-in-out infinite alternate;
  mix-blend-mode: screen;
}

.light-sweep {
  position: absolute;
  top: 0;
  right: -60%;
  width: 160%;
  height: 100%;
  background: linear-gradient(100deg, transparent 45%, rgba(255, 255, 255, 0.3) 50%, transparent 55%);
  filter: blur(60px);
  mix-blend-mode: screen;
  animation: sweep 12s ease-in-out infinite;
}
@keyframes sweep {
  0% { transform: translateX(80%); opacity: 0.05; }
  50% { transform: translateX(0%); opacity: 0.4; }
  100% { transform: translateX(-80%); opacity: 0.05; }
}

/* ✨ Text Glow */
@keyframes glow {
  0%, 100% { text-shadow: 0 0 30px rgba(0,255,200,0.3), 0 0 60px rgba(0,255,255,0.2); }
  50% { text-shadow: 0 0 50px rgba(0,255,255,0.6), 0 0 80px rgba(0,255,255,0.3); }
}
.animate-glow { animation: glow 4s ease-in-out infinite; }

/* 🌟 Feature Cards */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2.5rem;
  margin-top: 4rem;
}

.feature-card {
  position: relative;
  overflow: hidden;
  padding: 2.5rem;
  border-radius: 1.5rem;
  background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
  border: 1px solid rgba(0, 255, 200, 0.2);
  transition: all 0.5s ease;
  backdrop-filter: blur(10px);
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.03);
  border-color: rgba(0, 255, 200, 0.6);
  box-shadow: 0 15px 50px rgba(0, 255, 200, 0.3), 0 0 80px rgba(0, 255, 255, 0.15);
  background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
}

.feature-card .icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: #2dd4bf;
  text-shadow: 0 0 20px rgba(0, 255, 200, 0.6);
}

.feature-card h4 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #00e0b8;
}

.feature-card p {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #b0b0b0;
}

/* Parallax fog */
.parallax-fog {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 60% 50%, rgba(255,255,255,0.05), transparent 60%),
              radial-gradient(circle at 40% 60%, rgba(0,255,200,0.04), transparent 70%);
  filter: blur(80px);
  animation: parallaxFogMove 25s ease-in-out infinite alternate;
}
@keyframes parallaxFogMove {
  0% { transform: translate(0%, 0%) scale(1); }
  100% { transform: translate(-10%, 8%) scale(1.2); }
}
</style>