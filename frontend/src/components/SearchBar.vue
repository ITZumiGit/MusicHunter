<template>
  <div class="search-bar">
    <form class="input-wrap" @submit.prevent="submit">
      <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
      </svg>
      
      <input
        ref="inputRef"
        v-model="query"
        type="search"
        placeholder="Трек, артист..."
        :disabled="loading"
        autocomplete="off"
        autocorrect="off"
        autocapitalize="off"
        spellcheck="false"
        enterkeyhint="search"
      />
      
      <button v-if="query" class="clear" type="button" @click="clear">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      
      <button class="search-btn" type="submit" :disabled="!query.trim() || loading">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const props = defineProps<{ loading?: boolean }>()
const emit = defineEmits<{ search: [q: string] }>()

const query = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

function submit() {
  if (query.value.trim() && !props.loading) {
    emit('search', query.value.trim())
  }
}

function clear() {
  query.value = ''
  inputRef.value?.focus()
}

onMounted(() => { inputRef.value?.focus() })
</script>

<style scoped>
.search-bar { width: 100%; }

.input-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 0 var(--space-sm) 0 var(--space-md);
  height: 50px;
  transition: all var(--transition);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow), var(--shadow-glow);
}

.icon { flex-shrink: 0; color: var(--fg-muted); }

input {
  flex: 1; font-size: 15px; height: 100%;
  background: transparent; outline: none; border: none;
  color: var(--fg-primary); font-weight: 500;
}

input::placeholder { color: var(--fg-muted); }
input:disabled { opacity: 0.6; }
input[type="search"]::-webkit-search-cancel-button { -webkit-appearance: none; }

.clear {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: var(--radius-full);
  color: var(--fg-muted); transition: all var(--transition);
}

.clear:hover { background: var(--bg-tertiary); color: var(--fg-primary); }

.search-btn {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: var(--radius);
  background: var(--accent-gradient); color: white;
  transition: all var(--transition); flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.search-btn:hover:not(:disabled) { box-shadow: 0 4px 16px rgba(139, 92, 246, 0.4); }
.search-btn:active:not(:disabled) { transform: scale(0.92); }
.search-btn:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }
</style>
