<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const me = ref(null)
const errorMessage = ref('')

onMounted(async () => {
  const token = localStorage.getItem('accessToken')
  if (!token) {
    window.location.href = '/login'
    return
  }

  try {
    const res = await fetch(`${API_BASE_URL}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    const payload = await res.json().catch(() => ({}))
    if (!res.ok) {
      localStorage.removeItem('accessToken')
      window.location.href = '/login'
      return
    }

    me.value = payload
  } catch (e) {
    errorMessage.value = e?.message || '通信に失敗しました'
  }
})
</script>

<template>
  <div class="page">
    <h1>ダッシュボード</h1>
    <p class="lead">概要とクイックリンクです。</p>
    <p v-if="me" class="meta">ログイン中: {{ me.email }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <ul class="nav">
      <li><RouterLink to="/profile">プロフィール</RouterLink></li>
      <li><RouterLink to="/settings">設定</RouterLink></li>
    </ul>
  </div>
</template>

<style scoped>
.page {
  max-width: 36rem;
  margin: 0 auto;
  padding: 1.5rem;
}
.lead {
  color: var(--color-text);
  opacity: 0.85;
  margin-bottom: 1rem;
}
.meta {
  margin-bottom: 0.75rem;
  color: var(--color-text);
  opacity: 0.85;
}
.error {
  margin-bottom: 0.75rem;
  color: #b00020;
  font-size: 0.9rem;
}
.nav {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.nav a {
  color: var(--color-heading);
}
</style>
