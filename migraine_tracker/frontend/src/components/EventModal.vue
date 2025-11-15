<script setup>
const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  show: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close', 'edit']);
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="modal card">
      <h2>Migraine Details</h2>
      <p><strong>Start Time:</strong> {{ new Date(event.start_time).toLocaleString() }}</p>
      <p><strong>Intensity:</strong> {{ event.intensity }}</p>
      <p><strong>Pain Location:</strong> {{ event.pain_location.name }}</p>
      <p><strong>Symptoms:</strong> {{ event.symptoms.map(s => s.name).join(', ') }}</p>
      <p><strong>Triggers:</strong> {{ event.triggers.map(t => t.name).join(', ') }}</p>
      <p v-if="event.notes"><strong>Notes:</strong> {{ event.notes }}</p>
      <button @click="emit('close')">Close</button>
      <button class="edit-button" @click="emit('edit', event)">Edit</button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  max-width: 500px;
  width: 90%;
}

.edit-button {
  margin-left: 1rem;
}
</style>
