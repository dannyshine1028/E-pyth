<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="page">
    <h1>ダッシュボード</h1>
    <p class="lead">概要とクイックリンクです。</p>
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
