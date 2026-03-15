<template>
  <div class="pro-editor">
    <!-- ── Professional Toolbar ── -->
    <div class="pro-toolbar">
      <div class="toolbar-section">
        <button
          class="tb-btn" title="Gras"
          @click="editor?.chain().focus().toggleBold().run()"
          :class="{ active: editor?.isActive('bold') }"
        ><i class="bi bi-type-bold"></i></button>
        <button
          class="tb-btn" title="Italique"
          @click="editor?.chain().focus().toggleItalic().run()"
          :class="{ active: editor?.isActive('italic') }"
        ><i class="bi bi-type-italic"></i></button>
        <button
          class="tb-btn" title="Barré"
          @click="editor?.chain().focus().toggleStrike().run()"
          :class="{ active: editor?.isActive('strike') }"
        ><i class="bi bi-type-strikethrough"></i></button>
      </div>

      <span class="tb-divider"></span>

      <div class="toolbar-section">
        <button
          class="tb-btn tb-heading" title="Titre 1"
          @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
          :class="{ active: editor?.isActive('heading', { level: 1 }) }"
        >H1</button>
        <button
          class="tb-btn tb-heading" title="Titre 2"
          @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
          :class="{ active: editor?.isActive('heading', { level: 2 }) }"
        >H2</button>
        <button
          class="tb-btn tb-heading" title="Titre 3"
          @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
          :class="{ active: editor?.isActive('heading', { level: 3 }) }"
        >H3</button>
      </div>

      <span class="tb-divider"></span>

      <div class="toolbar-section">
        <button
          class="tb-btn" title="Liste à puces"
          @click="editor?.chain().focus().toggleBulletList().run()"
          :class="{ active: editor?.isActive('bulletList') }"
        ><i class="bi bi-list-ul"></i></button>
        <button
          class="tb-btn" title="Liste numérotée"
          @click="editor?.chain().focus().toggleOrderedList().run()"
          :class="{ active: editor?.isActive('orderedList') }"
        ><i class="bi bi-list-ol"></i></button>
      </div>

      <span class="tb-divider"></span>

      <div class="toolbar-section">
        <button
          class="tb-btn" title="Citation"
          @click="editor?.chain().focus().toggleBlockquote().run()"
          :class="{ active: editor?.isActive('blockquote') }"
        ><i class="bi bi-blockquote-left"></i></button>
        <button
          class="tb-btn" title="Bloc de code"
          @click="editor?.chain().focus().toggleCodeBlock().run()"
          :class="{ active: editor?.isActive('codeBlock') }"
        ><i class="bi bi-code-square"></i></button>
      </div>

      <span class="tb-divider"></span>

      <div class="toolbar-section">
        <button class="tb-btn" title="Image" @click="addImage">
          <i class="bi bi-image"></i>
        </button>
        <button class="tb-btn" title="YouTube" @click="addYoutubeVideo">
          <i class="bi bi-youtube"></i>
        </button>
        <button class="tb-btn" title="Lien" @click="addLink">
          <i class="bi bi-link-45deg"></i>
        </button>
      </div>

      <!-- Right side: undo/redo -->
      <div class="toolbar-right">
        <button class="tb-btn" title="Annuler" @click="editor?.chain().focus().undo().run()">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
        <button class="tb-btn" title="Rétablir" @click="editor?.chain().focus().redo().run()">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- ── Editor Content ── -->
    <div class="pro-content">
      <editor-content :editor="editor" v-if="editor" />
    </div>

    <!-- ── Status bar ── -->
    <div class="pro-statusbar">
      <span><i class="bi bi-fonts"></i> {{ wordCount }} mots</span>
      <span><i class="bi bi-clock"></i> ~{{ readingTime }} min de lecture</span>
      <span><i class="bi bi-paragraph"></i> {{ charCount }} caractères</span>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'ContentEditor',
}
</script>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Youtube from '@tiptap/extension-youtube'
import Placeholder from '@tiptap/extension-placeholder'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const plainText = ref('')

// Initialize editor
const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Image,
    Link.configure({ openOnClick: false }),
    Youtube,
    Placeholder.configure({
      placeholder: 'Commencez à rédiger votre contenu ici…'
    })
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
    plainText.value = editor.getText()
  }
})

// Stats
const wordCount = computed(() => {
  const text = plainText.value.trim()
  return text ? text.split(/\s+/).length : 0
})
const charCount = computed(() => plainText.value.length)
const readingTime = computed(() => Math.max(1, Math.ceil(wordCount.value / 200)))

// Watch for external changes to modelValue
watch(() => props.modelValue, (newContent) => {
  const currentContent = editor.value?.getHTML()
  if (editor.value && newContent !== currentContent) {
    editor.value.commands.setContent(newContent, false)
    plainText.value = editor.value.getText()
  }
}, { deep: true })

// Editor actions
const addImage = () => {
  const url = prompt('URL de l\'image:')
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
  }
}

const addYoutubeVideo = () => {
  const url = prompt('URL YouTube:')
  if (url && editor.value) {
    editor.value.chain().focus().setYoutubeVideo({ src: url }).run()
  }
}

const addLink = () => {
  const url = prompt('URL du lien:')
  if (url && editor.value) {
    editor.value.chain().focus().setLink({ href: url }).run()
  }
}

// Cleanup
onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped lang="scss">
$primary: #2453a7;
$primary-dark: #1a3f8a;
$primary-soft: #eaf2ff;
$dark: #1a2332;
$gray: #6b7280;
$gray-light: #f4f7fb;
$border: #dfe8f6;
$radius: 14px;
$radius-sm: 10px;

.pro-editor {
  border: 1px solid $border;
  border-radius: $radius;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 12px rgba(36,83,167,.07);
}

/* ── Toolbar ── */
.pro-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  padding: 10px 16px;
  background: $gray-light;
  border-bottom: 1px solid $border;
}
.toolbar-section {
  display: flex;
  align-items: center;
  gap: 2px;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: auto;
}
.tb-divider {
  width: 1px;
  height: 22px;
  background: $border;
  margin: 0 6px;
}
.tb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: $gray;
  font-size: .92rem;
  cursor: pointer;
  transition: .15s;
  &:hover {
    background: $primary-soft;
    color: $primary;
  }
  &.active {
    background: $primary;
    color: #fff;
  }
  &.tb-heading {
    font-size: .78rem;
    font-weight: 700;
    width: auto;
    padding: 0 10px;
    letter-spacing: -.02em;
  }
}

/* ── Content area ── */
.pro-content {
  min-height: 500px;
  padding: 32px 40px;
  background: #fff;
}

:deep(.ProseMirror) {
  outline: none;
  font-size: 1rem;
  line-height: 1.75;
  color: $dark;
  min-height: 450px;
}

:deep(.ProseMirror p) {
  margin-bottom: 1rem;
}

:deep(.ProseMirror h1) {
  font-size: 1.75rem;
  font-weight: 700;
  color: $dark;
  margin: 1.5rem 0 .75rem;
  line-height: 1.3;
}
:deep(.ProseMirror h2) {
  font-size: 1.35rem;
  font-weight: 700;
  color: $dark;
  margin: 1.25rem 0 .6rem;
  line-height: 1.35;
}
:deep(.ProseMirror h3) {
  font-size: 1.1rem;
  font-weight: 700;
  color: $dark;
  margin: 1rem 0 .5rem;
  line-height: 1.4;
}

:deep(.ProseMirror blockquote) {
  border-left: 4px solid $primary;
  background: $primary-soft;
  padding: 14px 20px;
  margin: 1rem 0;
  border-radius: 0 $radius-sm $radius-sm 0;
  color: $dark;
  font-style: italic;
}

:deep(.ProseMirror pre) {
  background: $dark;
  color: #e2e8f0;
  padding: 18px 22px;
  border-radius: $radius-sm;
  font-size: .88rem;
  line-height: 1.6;
  margin: 1rem 0;
  overflow-x: auto;
}

:deep(.ProseMirror code) {
  background: $primary-soft;
  color: $primary-dark;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: .88em;
}

:deep(.ProseMirror pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

:deep(.ProseMirror img) {
  max-width: 100%;
  height: auto;
  border-radius: $radius-sm;
  margin: 1rem 0;
}

:deep(.ProseMirror ul),
:deep(.ProseMirror ol) {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.ProseMirror li) {
  margin-bottom: .35rem;
}

:deep(.ProseMirror a) {
  color: $primary;
  text-decoration: underline;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: #b0b8c9;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.ProseMirror iframe) {
  border-radius: $radius-sm;
  margin: 1rem 0;
  max-width: 100%;
}

/* ── Status bar ── */
.pro-statusbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 20px;
  background: $gray-light;
  border-top: 1px solid $border;
  span {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: .75rem;
    color: $gray;
    i { font-size: .8rem; }
  }
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .pro-content { padding: 20px 16px; min-height: 350px; }
  :deep(.ProseMirror) { min-height: 300px; }
  .pro-toolbar { padding: 8px 10px; }
  .tb-divider { display: none; }
  .pro-statusbar { flex-wrap: wrap; gap: 12px; }
}
</style>