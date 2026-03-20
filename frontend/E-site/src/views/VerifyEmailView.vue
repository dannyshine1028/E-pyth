<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="page">
    <h1>メール確認</h1>
    <p class="lead">
      URL のクエリ（トークン）を読み取り、API で検証する処理をここに追加できます。
    </p>
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
.links a {
  color: var(--color-heading);
}
</style>
