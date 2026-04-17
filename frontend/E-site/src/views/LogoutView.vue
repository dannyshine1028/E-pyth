<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  localStorage.removeItem('accessToken')
  router.replace({ name: 'home' })
})
</script>

<template>
  <div class="page">
    <p>ログアウトしています…</p>
  </div>
</template>

<style scoped>
.page {
  padding: 1.5rem;
  text-align: center;
}
</style>
