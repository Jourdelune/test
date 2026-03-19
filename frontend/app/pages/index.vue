<script setup lang="ts">
import { ref, computed } from "vue";
import { useStream } from "@langchain/vue";
import { HumanMessage, AIMessage } from "langchain";
import type { UIMessage } from "ai";
import { PencilIcon, RotateCwIcon, SendIcon, SquareIcon } from "lucide-vue-next";

const input = ref("");
const editingId = ref<string | null>(null);
const editText = ref("");

const rawUrl = "http://localhost:2024";
const threadId = ref<string | null>(null);

const stream = useStream<{ messages: any[] }>({
  apiUrl: rawUrl,
  assistantId: "generalist",
  fetchStateHistory: true,
  reconnectOnMount: true,
  onThreadId: (id: string) => {
    threadId.value = id;
    console.log("Thread ID:", id);
  },
});

const streamedMessages = computed(() => stream.messages.value as UIMessage[]);
const history = stream.history ?? [];
const loading = computed(() => stream.isLoading.value);

function getMessageText(msg: UIMessage): string {
  if ("text" in msg && typeof msg.text === "string") {
    return msg.text;
  }
  if ("content" in msg) {
    if (typeof msg.content === "string") return msg.content;
    if (Array.isArray(msg.content)) {
      return msg.content
        .filter((b) => b.type === "text")
        .map((b: any) => b.text ?? "")
        .join("");
    }
  }
  return "";
}

function getParentCheckpoint(msg: UIMessage) {
  const meta = stream.getMessagesMetadata(msg);
  return meta?.firstSeenState?.parent_checkpoint;
}

function startEdit(msg: UIMessage) {
  if (stream.isLoading.value) return;
  editingId.value = msg.id;
  editText.value = getMessageText(msg);
}

function cancelEdit() {
  editingId.value = null;
  editText.value = "";
}

function getFirstCheckpointByMessageId(messageId: string) {
  if (!history.value) return null;

  for (const cp of history.value) {
    const messages = (cp.values?.messages ?? []) as any[];

    if (messages.some((m) => m.id === messageId)) {
      return cp; 
    }
  }

  return null;
}

function handleEdit(msg: UIMessage) {
  if (stream.isLoading.value) return;
  const newContent = editText.value.trim();

  if (!newContent) {
    cancelEdit();
    return;
  }

  const checkpoint = getFirstCheckpointByMessageId(msg.id!);
  if (!checkpoint) {
    console.log("No checkpoint found for message:", msg);
    cancelEdit();
    return;
  }

  console.log("Submitting edit with checkpoint:", checkpoint);

  cancelEdit();
  stream.submit(
    { messages: [{ ...msg, content: newContent }] },
    { checkpoint: checkpoint },
  );
}

function handleRegenerate(messageId: string) {
  if (stream.isLoading.value) return;
  const msg = streamedMessages.value.find((m) => m.id === messageId);
  if (!msg) return;
  console.log("Found message for regenerate:", msg);
  const checkpoint = getParentCheckpoint(msg);
  if (!checkpoint) {
    console.log("No checkpoint found for regenerate");
    return;
  }

  console.log("Regenerating from checkpoint:", checkpoint);
  stream.submit(undefined, { checkpoint });
}

function handleSubmit() {
  const text = input.value.trim();
  if (!text || stream.isLoading.value) return;

  stream.submit(
    { messages: [{ role: "human", content: text }] },
    {
      threadId: threadId.value ?? undefined,
      streamResumable: true,
    },
  );
  input.value = "";
}

function handleStop() {
  stream.stop();
}
</script>

<template>
  <div class="flex flex-col h-screen bg-background">
    <header class="border-b px-4 py-3">
      <h1 class="text-lg font-semibold">LangGraph Debug - Edit/Reload</h1>
      <p class="text-xs text-muted-foreground">Thread: {{ threadId || 'none' }}</p>
    </header>

    <main class="flex-1 overflow-y-auto px-4 py-8">
      <div class="max-w-3xl mx-auto space-y-4">
        <div v-if="streamedMessages.length === 0" class="text-center py-12">
          <p class="text-muted-foreground">Ask me anything.</p>
        </div>

        <div v-for="msg in streamedMessages" :key="msg.id" class="space-y-2">
          <p>
            (checkpoint {{ stream.getMessagesMetadata(msg)?.firstSeenState?.parent_checkpoint?.checkpoint_id }})
          </p>
          <div v-if="editingId === msg.id" class="flex justify-end">
            <div class="max-w-[80%] space-y-2">
              <textarea
                v-model="editText"
                class="w-full p-3 rounded-lg border bg-background"
                rows="3"
              />
              <div class="flex gap-2 justify-end">
                <button
                  class="px-3 py-1 text-sm border rounded hover:bg-muted"
                  @click="cancelEdit"
                >
                  Cancel
                </button>
                <button
                  class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  :disabled="!editText.trim()"
                  @click="handleEdit(msg)"
                >
                  Save
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="HumanMessage.isInstance(msg)" class="flex justify-end">
            <div class="max-w-[80%]">
              <div class="bg-blue-600 text-white rounded-lg px-4 py-2">
                {{ getMessageText(msg) }}
              </div>
              <div v-if="!loading" class="flex gap-1 mt-1 justify-end">
                <button
                  class="p-1 hover:bg-muted rounded"
                  title="Edit"
                  @click="startEdit(msg)"
                >
                  <PencilIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="AIMessage.isInstance(msg)" class="flex justify-start">
            <div class="max-w-[80%]">
              <div class="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
                {{ getMessageText(msg) }}
              </div>
              <div v-if="!loading" class="flex gap-1 mt-1">
                <button
                  class="p-1 hover:bg-muted rounded"
                  title="Regenerate"
                  @click="handleRegenerate(msg.id!)"
                >
                  <RotateCwIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="flex items-center gap-2 text-muted-foreground">
          <span class="animate-pulse">Thinking...</span>
        </div>
      </div>
    </main>

    <footer class="border-t p-4">
      <div class="max-w-3xl mx-auto flex gap-2">
        <textarea
          v-model="input"
          class="flex-1 p-3 rounded-lg border bg-background resize-none"
          rows="2"
          placeholder="Ask me anything..."
          @keydown.enter.exact.prevent="handleSubmit"
        />
        <button
          v-if="loading"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
          @click="handleStop"
        >
          <SquareIcon class="w-5 h-5" />
        </button>
        <button
          v-else
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          @click="handleSubmit"
        >
          <SendIcon class="w-5 h-5" />
        </button>
      </div>
    </footer>
  </div>
</template>
