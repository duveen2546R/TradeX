<template>
  <main class="auth-shell">
    <div class="aurora"><i></i><i></i><i></i></div>
    <section class="auth-card">
      <p class="eyebrow">TradeX</p>
      <h1>{{ mode === 'login' ? 'Welcome back' : 'Start paper trading' }}</h1>
      <p class="subtle">{{ mode === 'login' ? 'Sign in to your virtual portfolio.' : 'Create an account and receive ₹10,00,000 virtual cash.' }}</p>
      <form @submit.prevent="submit">
        <label>Email<input v-model.trim="email" type="email" autocomplete="email" required /></label>
        <label>Password<input v-model="password" type="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" minlength="8" required /></label>
        <p v-if="error" class="error">{{ error }}</p>
        <button :disabled="loading">{{ loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account' }}</button>
      </form>
      <button class="link" @click="mode = mode === 'login' ? 'register' : 'login'; error = ''">
        {{ mode === 'login' ? 'Need an account? Register' : 'Already registered? Sign in' }}
      </button>
    </section>
  </main>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();
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

<style scoped>
.auth-shell { min-height:100vh; isolation:isolate; display:grid; place-items:center; overflow:hidden; padding:24px; color:#e5e7eb; background:#05090e; font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }.aurora { position:absolute; inset:0; z-index:-1; overflow:hidden; background:radial-gradient(circle at 50% 0%,#0d2e37aa,transparent 45%); }.aurora i { position:absolute; display:block; border-radius:999px; filter:blur(80px); opacity:.42; animation:float 18s ease-in-out infinite alternate; }.aurora i:nth-child(1){width:35rem;height:35rem;top:-18rem;left:-10rem;background:#14b8a6;}.aurora i:nth-child(2){width:30rem;height:30rem;right:-12rem;bottom:-15rem;background:#2563eb;animation-delay:-6s;}.aurora i:nth-child(3){width:18rem;height:18rem;left:40%;bottom:5%;background:#0891b2;animation-delay:-11s;}@keyframes float{to{transform:translate(90px,50px) scale(1.1)}}
.auth-card { width:min(100%,430px); padding:40px; border:1px solid rgba(45,212,191,.28); border-radius:28px; background:linear-gradient(145deg,rgba(22,27,34,.82),rgba(6,16,24,.76)); box-shadow:0 28px 90px #000a, inset 0 1px #ffffff10; backdrop-filter:blur(20px); }.eyebrow { margin:0; color:#2dd4bf; font-weight:800; letter-spacing:.16em; text-transform:uppercase; font-size:.76rem; }.auth-card h1 { margin:10px 0; font-size:2.35rem; letter-spacing:-.05em; }.subtle { color:#9ca3af; line-height:1.6; } form { display:grid; gap:16px; margin-top:28px; } label { display:grid; gap:8px; font-size:.85rem; font-weight:600; color:#cbd5e1; } input { border:1px solid #334155; border-radius:14px; padding:13px 14px; outline:0; background:#081119cc; color:#f8fafc; transition:.2s; } input:focus { border-color:#2dd4bf; box-shadow:0 0 0 4px #2dd4bf22; } button { border:0; border-radius:999px; padding:13px 18px; background:linear-gradient(90deg,#14b8a6,#22d3ee); color:#042f2e; font-weight:800; cursor:pointer; box-shadow:0 8px 24px #14b8a644; transition:.2s; } button:hover { transform:translateY(-1px); filter:brightness(1.06); } button:disabled { opacity:.6; cursor:wait; }.link { width:100%; margin-top:16px; color:#5eead4; background:transparent; box-shadow:none; }.error { margin:0; padding:10px 12px; border-radius:10px; color:#fecaca; background:#7f1d1d55; }
</style>
