<template>
  <main class="success">
    <div class="inner">
      <div class="sparkle" aria-hidden="true">
        <span>✨</span>
      </div>
      <h2>Added to the memories!</h2>
      <div class="gold-rule" />
      <p class="lede">Thank you for capturing this moment.</p>
      <RouterLink to="/capture" class="cta" @click.native="reset">Take another 📸</RouterLink>
      <RouterLink to="/gallery" class="ghost">View the gallery →</RouterLink>
    </div>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { clearPending } from '../router.js'

function reset () {
  clearPending()
}

onMounted(() => {
  // clear old blob URLs
  clearPending()
})
</script>

<style scoped>
.success {
  min-height: 100dvh;
  background:
    radial-gradient(circle at 50% 30%, rgba(212, 175, 55, 0.12), transparent 60%),
    #000;
  color: #fff;
  display: grid;
  place-items: center;
  padding: 3rem 1.5rem;
}
.inner {
  max-width: 26rem;
  text-align: center;
}
.sparkle {
  font-size: 3rem;
  margin: 0 0 1.5rem;
  animation: pop 0.65s ease-out both;
}
@keyframes pop {
  0% { transform: scale(0.2) rotate(-10deg); opacity: 0; }
  60% { transform: scale(1.15) rotate(4deg); opacity: 1; }
  100% { transform: scale(1) rotate(0); }
}
h2 {
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(1.9rem, 7vw, 2.4rem);
  margin: 0;
}
.gold-rule {
  width: 3rem;
  height: 2px;
  background: var(--gold);
  margin: 1rem auto 1.5rem;
}
.lede {
  color: rgba(255, 255, 255, 0.75);
  margin: 0 0 2.5rem;
}
.cta {
  display: block;
  padding: 1rem;
  background: var(--gold);
  color: #000;
  border-radius: 999px;
  font-weight: 600;
  text-decoration: none;
  letter-spacing: 0.05em;
}
.ghost {
  display: inline-block;
  margin-top: 1rem;
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  border-bottom: 1px solid rgba(212, 175, 55, 0.35);
  padding-bottom: 2px;
}
</style>
