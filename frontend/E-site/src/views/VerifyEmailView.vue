<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const token = computed(() => String(route.query.token || ''))

const errorMessage = ref('')
const isVerifying = ref(false)

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const verify = async () => {
  errorMessage.value = ''
  isVerifying.value = true
  try {
    if (!token.value) {
      errorMessage.value = 'トークンがありません。最初からやり直してください。'
      return
    }

    const res = await fetch(`${API_BASE_URL}/auth/verify-email`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ token: token.value }),
    })

    const payload = await res.json().catch(() => ({}))
    if (!res.ok) {
      errorMessage.value = payload?.detail || 'メール認証に失敗しました'
      return
    }

    if (payload?.next === 'profile') {
      window.location.href = `/profile?token=${encodeURIComponent(payload.flowToken || '')}`
      return
    }

    window.location.href = '/dashboard'
  } catch (e) {
    errorMessage.value = e?.message || '通信に失敗しました'
  } finally {
    isVerifying.value = false
  }
}

onMounted(() => {
  if (token.value) verify()
})
</script>

<template>
  <div class="page">
    <h1>メール確認</h1>
    <p class="lead">このトークンでメール認証を行います。</p>

    <p v-if="!token" class="note">
      メールに届く認証リンクからアクセスしてください。
    </p>

    <button
      v-else
      class="btn"
      type="button"
      :disabled="isVerifying"
      @click="verify"
    >
      {{ isVerifying ? '認証中...' : '認証する' }}
    </button>

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
  margin-bottom: 1rem;
}
.btn {
  margin-top: 0.5rem;
  width: 100%;
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
  margin-top: 0.75rem;
  color: var(--color-text);
  opacity: 0.85;
}
.links a {
  color: var(--color-heading);
}
</style>
