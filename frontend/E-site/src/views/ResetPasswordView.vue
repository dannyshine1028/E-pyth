<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="page">
    <h1>新しいパスワード</h1>
    <p class="lead">メールのトークンと合わせてバックエンドと接続します。</p>
    <form class="form" @submit.prevent>
      <label>
        新しいパスワード
        <input type="password" name="password" autocomplete="new-password" />
      </label>
      <label>
        確認
        <input type="password" name="password_confirm" autocomplete="new-password" />
      </label>
      <button type="submit">更新</button>
    </form>
    <p class="links">
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
</style>
