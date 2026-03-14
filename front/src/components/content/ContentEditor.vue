<template>
  <div class="content-editor">
    <!-- Editor Toolbar -->
    <div class="editor-toolbar bg-white border-bottom p-2 sticky-top">
      <div class="btn-toolbar" role="toolbar">
        <div class="btn-group me-2">
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleBold().run()"
            :class="{ active: editor?.isActive('bold') }"
          >
            <i class="bi bi-type-bold"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleItalic().run()"
            :class="{ active: editor?.isActive('italic') }"
          >
            <i class="bi bi-type-italic"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleStrike().run()"
            :class="{ active: editor?.isActive('strike') }"
          >
            <i class="bi bi-type-strikethrough"></i>
          </button>
        </div>

        <div class="btn-group me-2">
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
            :class="{ active: editor?.isActive('heading', { level: 1 }) }"
          >
            H1
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
            :class="{ active: editor?.isActive('heading', { level: 2 }) }"
          >
            H2
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
            :class="{ active: editor?.isActive('heading', { level: 3 }) }"
          >
            H3
          </button>
        </div>

        <div class="btn-group me-2">
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleBulletList().run()"
            :class="{ active: editor?.isActive('bulletList') }"
          >
            <i class="bi bi-list-ul"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleOrderedList().run()"
            :class="{ active: editor?.isActive('orderedList') }"
          >
            <i class="bi bi-list-ol"></i>
          </button>
        </div>

        <div class="btn-group me-2">
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleBlockquote().run()"
            :class="{ active: editor?.isActive('blockquote') }"
          >
            <i class="bi bi-blockquote-left"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="editor?.chain().focus().toggleCodeBlock().run()"
            :class="{ active: editor?.isActive('codeBlock') }"
          >
            <i class="bi bi-code-square"></i>
          </button>
        </div>

        <div class="btn-group me-2">
          <button 
            class="btn btn-outline-secondary"
            @click="addImage"
          >
            <i class="bi bi-image"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="addYoutubeVideo"
          >
            <i class="bi bi-youtube"></i>
          </button>
          <button 
            class="btn btn-outline-secondary"
            @click="addLink"
          >
            <i class="bi bi-link-45deg"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="editor-content p-3">
      <editor-content :editor="editor" v-if="editor" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
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

// Initialize editor
const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Image,
    Link,
    Youtube,
    Placeholder.configure({
      placeholder: 'Commencez à écrire...'
    })
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  }
})

// Watch for external changes to modelValue
watch(() => props.modelValue, (newContent) => {
  const currentContent = editor.value?.getHTML()
  if (editor.value && newContent !== currentContent) {
    editor.value.commands.setContent(newContent, false)
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

<style scoped>
.content-editor {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

.editor-toolbar {
  border-top-left-radius: 0.25rem;
  border-top-right-radius: 0.25rem;
}

.editor-content {
  min-height: 400px;
}

:deep(.ProseMirror) {
  outline: none;
}

:deep(.ProseMirror p) {
  margin-bottom: 1rem;
}

:deep(.ProseMirror h1),
:deep(.ProseMirror h2),
:deep(.ProseMirror h3) {
  margin-bottom: 1rem;
  font-weight: 600;
}

:deep(.ProseMirror blockquote) {
  border-left: 3px solid #dee2e6;
  padding-left: 1rem;
  margin-left: 0;
  margin-right: 0;
}

:deep(.ProseMirror pre) {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.25rem;
}

:deep(.ProseMirror img) {
  max-width: 100%;
  height: auto;
}

.btn-group .btn.active {
  background-color: var(--bs-primary);
  color: white;
  border-color: var(--bs-primary);
}
</style>