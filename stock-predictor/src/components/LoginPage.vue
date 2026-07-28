<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useTheme } from "../composables/useTheme";

const router = useRouter();
const { theme, toggleTheme } = useTheme();
const mode = ref("login");
const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  loading.value = true;
  error.value = "";
  try {
    await api.post(`/api/auth/${mode.value === 'login' ? 'login' : 'register'}`, { email: email.value, password: password.value });
    router.replace("/dashboard");
  } catch (err) {
    error.value = err.response?.data?.error || "Unable to continue. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex w-full bg-white dark:bg-black font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
    <!-- Left Branded Panel (Hidden on mobile, 50% width on desktop) -->
    <div class="hidden lg:flex w-1/2 bg-gradient-to-br from-emerald-500 to-teal-600 p-12 flex-col justify-between text-white relative">
      <!-- Theme toggle on branded panel -->
      <div>
        <h1 class="text-3xl font-bold tracking-tight">TradeX</h1>
        <p class="mt-4 text-emerald-100 text-lg max-w-sm">
          The ultimate platform for intelligent stock prediction and portfolio management.
        </p>
      </div>

      <div class="space-y-8">
        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-white/20">
            <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold">Real-time Insights</h3>
            <p class="mt-1 text-emerald-100 text-sm">Stay ahead with lightning-fast market data and analytics.</p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-white/20">
            <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold">Bank-grade Security</h3>
            <p class="mt-1 text-emerald-100 text-sm">Your data and portfolio are fully encrypted and secure.</p>
          </div>
        </div>

        <div class="flex items-start space-x-4">
          <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-white/20">
            <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold">24/7 Monitoring</h3>
            <p class="mt-1 text-emerald-100 text-sm">Automated alerts keep you informed around the clock.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Form Panel -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-16 relative">
      <!-- Theme toggle -->
      <button @click="toggleTheme" class="absolute top-6 right-6 theme-toggle" :title="theme === 'dark' ? 'Switch to light' : 'Switch to dark'">
        <svg v-if="theme === 'dark'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="5" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" d="M12 1v2m0 18v2m11-11h-2M3 12H1m16.36-7.36l-1.41 1.41M6.05 17.95l-1.41 1.41m12.72 0l-1.41-1.41M6.05 6.05L4.64 4.64"/></svg>
        <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>

      <div class="w-full max-w-md space-y-8">
        <div>
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            {{ mode === 'login' ? 'Welcome back' : 'Create your account' }}
          </h2>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {{ mode === 'login' ? 'Enter your details to access your portfolio.' : 'Sign up to start tracking and predicting stocks.' }}
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="submit">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email address</label>
            <div class="mt-1">
              <input 
                id="email" 
                name="email" 
                type="email" 
                v-model="email" 
                autocomplete="email" 
                required 
                class="appearance-none block w-full px-4 py-3 border border-gray-200 dark:border-[#1a1a1a] rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-600 bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-white focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition-colors"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <div class="mt-1">
              <input 
                id="password" 
                name="password" 
                type="password" 
                v-model="password" 
                autocomplete="current-password" 
                required 
                class="appearance-none block w-full px-4 py-3 border border-gray-200 dark:border-[#1a1a1a] rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-600 bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-white focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div v-if="error" class="rounded-md bg-red-50 dark:bg-red-950/50 p-4 border border-red-100 dark:border-red-900/50">
            <div class="flex">
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-400">{{ error }}</h3>
              </div>
            </div>
          </div>

          <div>
            <button 
              type="submit" 
              :disabled="loading"
              class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-black dark:bg-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black dark:focus:ring-white transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Processing...' : (mode === 'login' ? 'Sign in' : 'Create account') }}
            </button>
          </div>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ mode === 'login' ? "Don't have an account?" : "Already have an account?" }}
            <button 
              @click="mode = mode === 'login' ? 'register' : 'login'" 
              type="button"
              class="font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 focus:outline-none transition-colors ml-1"
            >
              {{ mode === 'login' ? 'Sign up' : 'Log in' }}
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
