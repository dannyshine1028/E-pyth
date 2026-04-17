<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const token = ref(String(route.query.token || ''))

const displayName = ref('')
const info = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const submit = async () => {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    if (!token.value) {
      errorMessage.value = 'トークンがありません。最初からやり直してください。'
      return
    }

    const res = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        token: token.value,
        displayName: displayName.value,
        info: info.value,
      }),
    })

    const payload = await res.json().catch(() => ({}))
    if (!res.ok) {
      errorMessage.value = payload?.detail || '情報の保存に失敗しました'
      return
    }

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
    <h1>情報入力</h1>
    <p class="lead">この後にダッシュボードへ移動します。</p>

    <p v-if="!token" class="note">
      トークンがありません。ログインからやり直してください。
    </p>

    <form v-else class="form" @submit.prevent="submit">
      <label>
        表示名
        <input v-model="displayName" type="text" name="displayName" />
      </label>
      <label>
        自己紹介
        <textarea v-model="info" name="info" rows="4" />
      </label>
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '保存中...' : '保存' }}
      </button>
    </form>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <p class="links">
      <RouterLink to="/login">ログインへ</RouterLink>
    </p>
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
.form input,
.form textarea {
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text);
}
.form textarea {
  resize: vertical;
}
.form button {
  padding: 0.7rem 1rem;
  cursor: pointer;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-background-soft);
  color: var(--color-text);
}
.error {
  margin-top: 1rem;
  color: #b00020;
  font-size: 0.9rem;
}
.note {
  margin-top: 1rem;
  color: var(--color-text);
  opacity: 0.85;
}
.links a {
  color: var(--color-heading);
}
</style>
