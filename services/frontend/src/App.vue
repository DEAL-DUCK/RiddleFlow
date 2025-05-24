<!-- src/App.vue -->
<template>
  <div>
    <AppNavbar />
    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>

<script>
import AppNavbar from '@/components/NavBar.vue';

export default {
  components: {
    AppNavbar
  }
};
</script>

<style>
@import '../node_modules/bootstrap-icons/font/bootstrap-icons.css';
</style>