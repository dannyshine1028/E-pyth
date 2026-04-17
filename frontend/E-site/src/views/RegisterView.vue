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
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })

    const payload = await res.json().catch(() => ({}))
    if (!res.ok) {
      errorMessage.value = payload?.detail || '登録に失敗しました'
      return
    }

    // 登録後は本人確認が必要なので、メールリンクから認証してからログインする
    window.location.href = '/verify-email'
  } catch (e) {
    errorMessage.value = e?.message || '通信に失敗しました'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>新規登録</h1>
    <p class="lead">アカウントを作成します。</p>
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
          autocomplete="new-password"
        />
      </label>
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '登録中...' : '登録' }}
      </button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p class="links">
      すでにアカウントがある方は
      <RouterLink to="/login">ログイン</RouterLink>
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
