<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, nextTick } from 'vue'

type RawOption = string | number | Record<string, any>

const props = withDefaults(defineProps<{
  modelValue: string | number | boolean | null | undefined
  options: RawOption[]
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  searchable?: boolean
  creatable?: boolean
  labelKey?: string
  valueKey?: string
  invalid?: boolean
  size?: 'sm' | 'md' | 'lg'
  id?: string
}>(), {
  placeholder: 'Sélectionner…',
  disabled: false,
  clearable: false,
  searchable: true,
  creatable: false,
  labelKey: 'label',
  valueKey: 'value',
  invalid: false,
  size: 'md',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number | boolean | null): void
  (e: 'create', value: string): void
}>()

interface NormOption { value: string | number | boolean; label: string }

const normalized = computed<NormOption[]>(() =>
  (props.options || []).map((opt) => {
    if (opt !== null && typeof opt === 'object') {
      return { value: opt[props.valueKey], label: String(opt[props.labelKey] ?? opt[props.valueKey] ?? '') }
    }
    return { value: opt as string | number, label: String(opt) }
  })
)

const open = ref(false)
const search = ref('')
const highlighted = ref(0)
const rootEl = ref<HTMLElement | null>(null)
const searchEl = ref<HTMLInputElement | null>(null)

const selectedLabel = computed(() => {
  const found = normalized.value.find((o) => o.value === props.modelValue)
  return found ? found.label : ''
})

const filtered = computed(() => {
  if (!props.searchable || !search.value.trim()) return normalized.value
  const q = search.value.trim().toLowerCase()
  return normalized.value.filter((o) => o.label.toLowerCase().includes(q))
})

const showCreate = computed(() => {
  if (!props.creatable || !search.value.trim()) return false
  const q = search.value.trim().toLowerCase()
  return !normalized.value.some((o) => o.label.toLowerCase() === q)
})

const toggle = () => {
  if (props.disabled) return
  open.value ? close() : openMenu()
}

const openMenu = async () => {
  open.value = true
  search.value = ''
  highlighted.value = Math.max(0, filtered.value.findIndex((o) => o.value === props.modelValue))
  await nextTick()
  searchEl.value?.focus()
}

const close = () => {
  open.value = false
  search.value = ''
}

const pick = (opt: NormOption) => {
  emit('update:modelValue', opt.value)
  close()
}

const clear = (e: Event) => {
  e.stopPropagation()
  emit('update:modelValue', null)
}

const create = () => {
  const value = search.value.trim()
  if (!value) return
  emit('create', value)
  close()
}

const onKeydown = (e: KeyboardEvent) => {
  if (!open.value) {
    if (e.key === 'Enter' || e.key === 'ArrowDown' || e.key === ' ') {
      e.preventDefault()
      openMenu()
    }
    return
  }
  const max = filtered.value.length + (showCreate.value ? 1 : 0)
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    highlighted.value = Math.min(highlighted.value + 1, max - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    highlighted.value = Math.max(highlighted.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (showCreate.value && highlighted.value === filtered.value.length) {
      create()
    } else if (filtered.value[highlighted.value]) {
      pick(filtered.value[highlighted.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    close()
  }
}

watch(search, () => { highlighted.value = 0 })

const onClickOutside = (e: MouseEvent) => {
  if (rootEl.value && !rootEl.value.contains(e.target as Node)) close()
}
watch(open, (v) => {
  if (v) document.addEventListener('mousedown', onClickOutside)
  else document.removeEventListener('mousedown', onClickOutside)
})
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<template>
  <div ref="rootEl" class="ss-root" :class="[`ss-${size}`, { 'ss-open': open, 'ss-disabled': disabled, 'ss-invalid': invalid }]">
    <button
      type="button"
      class="ss-control"
      :id="id"
      :disabled="disabled"
      @click="toggle"
      @keydown="onKeydown"
    >
      <span class="ss-value" :class="{ 'ss-placeholder': !selectedLabel }">
        {{ selectedLabel || placeholder }}
      </span>
      <span v-if="clearable && selectedLabel && !disabled" class="ss-clear" @click="clear" aria-label="Effacer">
        <i class="bi bi-x-lg"></i>
      </span>
      <i class="bi bi-chevron-down ss-caret"></i>
    </button>

    <div v-if="open" class="ss-menu">
      <div v-if="searchable" class="ss-search">
        <i class="bi bi-search"></i>
        <input
          ref="searchEl"
          v-model="search"
          type="text"
          class="ss-search-input"
          placeholder="Rechercher…"
          @keydown="onKeydown"
        >
      </div>
      <ul class="ss-options" role="listbox">
        <li
          v-for="(opt, i) in filtered"
          :key="String(opt.value)"
          class="ss-option"
          :class="{ 'ss-active': i === highlighted, 'ss-selected': opt.value === modelValue }"
          role="option"
          :aria-selected="opt.value === modelValue"
          @mouseenter="highlighted = i"
          @click="pick(opt)"
        >
          <span class="ss-option-label">{{ opt.label }}</span>
          <i v-if="opt.value === modelValue" class="bi bi-check2 ss-check"></i>
        </li>

        <li
          v-if="showCreate"
          class="ss-option ss-create"
          :class="{ 'ss-active': highlighted === filtered.length }"
          @mouseenter="highlighted = filtered.length"
          @click="create"
        >
          <i class="bi bi-plus-circle"></i>
          <span>Ajouter «&nbsp;{{ search.trim() }}&nbsp;»</span>
        </li>

        <li v-if="!filtered.length && !showCreate" class="ss-empty">
          Aucun résultat
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.ss-root {
  position: relative;
  width: 100%;
  font-size: 0.9rem;
}
.ss-control {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 0.75rem;
  background: #fff;
  border: 1px solid #ced4da;
  border-radius: 8px;
  color: #212529;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, box-shadow 0.15s;
  min-height: 40px;
}
.ss-sm .ss-control { padding: 0.35rem 0.6rem; min-height: 34px; font-size: 0.82rem; }
.ss-lg .ss-control { padding: 0.65rem 0.9rem; min-height: 46px; font-size: 1rem; }
.ss-control:focus {
  outline: none;
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.2);
}
.ss-open .ss-control {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.2);
}
.ss-invalid .ss-control {
  border-color: #dc3545;
}
.ss-invalid.ss-open .ss-control,
.ss-invalid .ss-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.2);
}
.ss-disabled .ss-control {
  background: #e9ecef;
  cursor: not-allowed;
  opacity: 0.7;
}
.ss-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ss-placeholder { color: #6c757d; }
.ss-caret {
  font-size: 0.7rem;
  color: #6c757d;
  transition: transform 0.2s;
  flex-shrink: 0;
}
.ss-open .ss-caret { transform: rotate(180deg); }
.ss-clear {
  display: inline-flex;
  align-items: center;
  color: #adb5bd;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.ss-clear:hover { color: #dc3545; }

.ss-menu {
  position: absolute;
  z-index: 1060;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e6ef;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}
.ss-search {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-bottom: 1px solid #eef2f7;
  color: #6c757d;
}
.ss-search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.85rem;
  color: #212529;
  background: transparent;
}
.ss-options {
  list-style: none;
  margin: 0;
  padding: 4px;
  max-height: 240px;
  overflow-y: auto;
}
.ss-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: #333;
}
.ss-option-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ss-option.ss-active { background: #f0f4ff; color: #2453a7; }
.ss-option.ss-selected { font-weight: 600; }
.ss-check { color: #2453a7; font-size: 0.85rem; }
.ss-create { color: #2453a7; font-weight: 600; }
.ss-create.ss-active { background: #eaf2ff; }
.ss-empty {
  padding: 12px 10px;
  text-align: center;
  color: #adb5bd;
  font-size: 0.82rem;
}
.ss-options::-webkit-scrollbar { width: 8px; }
.ss-options::-webkit-scrollbar-thumb { background: #d5deea; border-radius: 8px; }
</style>
