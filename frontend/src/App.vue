<script setup>
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <app-header />
  <main class="app-shell">
    <router-view />
  </main>
</template>
