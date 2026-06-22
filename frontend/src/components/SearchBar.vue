<template>
  <div class="search-bar">
    <div class="input-wrap">
      <!-- Search icon -->
      <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
      </svg>
      
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Поиск музыки..."
        @keydown.enter="submit"
        :disabled="loading"
      />
      
      <button v-if="query" class="clear" @click="clear">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
      
      <div v-if="loading" class="spinner"></div>
    </div>
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

// Auto-focus on mount
onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.search-bar {
  width: 100%;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0 var(--space-md);
  height: 48px;
  transition: all var(--transition);
}

.input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.icon {
  flex-shrink: 0;
  color: var(--fg-muted);
}

input {
  flex: 1;
  font-size: 15px;
  height: 100%;
  background: transparent;
}

input::placeholder {
  color: var(--fg-muted);
}

input:disabled {
  opacity: 0.6;
}

.clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  color: var(--fg-muted);
  transition: all var(--transition);
}

.clear:hover {
  background: var(--bg-tertiary);
  color: var(--fg-primary);
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
