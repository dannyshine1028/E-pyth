<script setup>
import { RouterLink } from 'vue-router'
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const submit = async () => {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })

    const payload = await res.json().catch(() => ({}))
    if (!res.ok) {
      if (res.status === 403 && payload?.detail === 'email not verified') {
        errorMessage.value =
          'メール認証が完了していません。届いたメールのリンクを開いてください。'
      } else {
        errorMessage.value = payload?.detail || 'ログインに失敗しました'
      }
      return
    }

    const accessToken = payload?.accessToken
    if (!accessToken) {
      errorMessage.value = 'ログイン応答が不正です'
      return
    }

    localStorage.setItem('accessToken', String(accessToken))

    window.location.href = '/dashboard'
  } catch (e) {
    errorMessage.value = e?.message || '通信に失敗しました'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>ログイン</h1>
    <p class="lead">アカウントでサインインします。</p>
    <form class="form" @submit.prevent="submit">
      <label>
        メール
        <input
          v-model="email"
          type="email"
          name="email"
          autocomplete="username"
        />
      </label>
      <label>
        パスワード
        <input
          v-model="password"
          type="password"
          name="password"
          autocomplete="current-password"
        />
      </label>
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'ログイン中...' : 'ログイン' }}
      </button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p class="links">
      <RouterLink to="/register">新規登録</RouterLink>
      ·
      <RouterLink to="/forgot-password">パスワードを忘れた</RouterLink>
    </p>
  </div>
</template>

<style scoped>
.page {
  max-width: 24rem;
  margin: 0 auto;
  padding: 1.5rem;
}
.lead {
  color: var(--color-text);
  opacity: 0.85;
  margin-bottom: 1.25rem;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
}
.form input {
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text);
}
.form button {
  margin-top: 0.25rem;
  padding: 0.55rem 1rem;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
  color: var(--color-text);
}
.links {
  margin-top: 1.25rem;
  font-size: 0.9rem;
}
.links a {
  color: var(--color-heading);
}

.error {
  margin-top: 1rem;
  color: #b00020;
  font-size: 0.9rem;
}
</style>
