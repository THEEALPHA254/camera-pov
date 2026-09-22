<template>
  <main class="landing">
    <div class="cover">
      <p class="eyebrow">{{ headline }}</p>
      <h1 class="title">Capture <span class="ital">the</span> Moment</h1>
      <div class="gold-rule" />
      <p class="lede">
        Your perspective matters. Take a photo and add it to
        {{ hostPossessive }} graduation memories.
      </p>
      <RouterLink to="/capture" class="cta">📸&nbsp; SNAP IT</RouterLink>
      <RouterLink to="/gallery" class="ghost">🖼️ &nbsp;View Gallery</RouterLink>
      <p v-if="eventDate" class="date">{{ eventDate }}</p>
    </div>
  </main>
</template>

<script setup>
const headline = import.meta.env.VITE_EVENT_HEADLINE || 'GRACE IS GRADUATING 🎓'
const host = import.meta.env.VITE_EVENT_HOST || 'our'
const eventDate = import.meta.env.VITE_EVENT_DATE || ''
const hostPossessive = host.endsWith('s') ? `${host}'` : `${host}'s`
</script>

<style scoped>
.landing {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  padding: 3rem 1.5rem;
  background:
    radial-gradient(circle at 50% 0%, rgba(212, 175, 55, 0.08), transparent 60%),
    #000;
}
.cover {
  max-width: 30rem;
  text-align: center;
}
.eyebrow {
  color: var(--gold);
  letter-spacing: 0.24em;
  font-size: 0.82rem;
  margin: 0 0 2rem;
  font-weight: 600;
}
.title {
  font-family: var(--serif);
  color: #fff;
  font-size: clamp(2.5rem, 8vw, 3.6rem);
  font-weight: 500;
  line-height: 1.05;
  margin: 0;
}
.ital {
  font-style: italic;
  color: var(--gold);
  font-weight: 500;
}
.gold-rule {
  width: 3.5rem;
  height: 2px;
  background: var(--gold);
  margin: 1.75rem auto;
}
.lede {
  color: rgba(255, 255, 255, 0.78);
  font-size: 1rem;
  line-height: 1.55;
  margin: 0 0 2.75rem;
}
.cta {
  display: block;
  padding: 1.1rem 1rem;
  background: var(--gold);
  color: #000;
  border: none;
  border-radius: 999px;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-decoration: none;
  box-shadow: 0 10px 30px rgba(212, 175, 55, 0.25);
}
.cta:active {
  transform: translateY(1px);
  box-shadow: 0 6px 18px rgba(212, 175, 55, 0.25);
}
.ghost {
  display: inline-block;
  margin-top: 1.25rem;
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-size: 0.95rem;
  border-bottom: 1px solid rgba(212, 175, 55, 0.35);
  padding-bottom: 2px;
}
.date {
  margin-top: 3rem;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 0.14em;
  font-size: 0.8rem;
}
</style>
