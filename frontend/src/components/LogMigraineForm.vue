<script setup>
import { ref, onMounted, watch } from 'vue';
import VueMultiselect from 'vue-multiselect';
import axios from 'axios';

const props = defineProps({
  eventToEdit: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['migraine-logged']);

const painLocation = ref('');
const symptoms = ref([]);
const intensity = ref(5);
const startTime = ref(new Date().toISOString().slice(0, 16));
const endTime = ref('');
const triggers = ref([]);
const notes = ref('');
const error = ref(null);
const isLoading = ref(false);

const painLocationOptions = ref([]);
const symptomOptions = ref([]);
const triggerOptions = ref([]);

const fetchOptions = async () => {
  try {
    const [painLocationsRes, symptomsRes, triggersRes] = await Promise.all([
      axios.get('/api/pain_locations/'),
      axios.get('/api/symptoms/'),
      axios.get('/api/triggers/'),
    ]);
    painLocationOptions.value = painLocationsRes.data.map(item => item.name);
    symptomOptions.value = symptomsRes.data.map(item => item.name);
    triggerOptions.value = triggersRes.data.map(item => item.name);
  } catch (err) {
    console.error('Failed to fetch options:', err);
  }
};

onMounted(fetchOptions);

watch(() => props.eventToEdit, (newEvent) => {
  if (newEvent) {
    painLocation.value = newEvent.pain_location.name;
    symptoms.value = newEvent.symptoms.map(s => s.name);
    intensity.value = newEvent.intensity;
    startTime.value = new Date(newEvent.start_time).toISOString().slice(0, 16);
    endTime.value = newEvent.end_time ? new Date(newEvent.end_time).toISOString().slice(0, 16) : '';
    triggers.value = newEvent.triggers.map(t => t.name);
    notes.value = newEvent.notes;
  }
}, { immediate: true });

const handleSubmit = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    const formData = {
      start_time: startTime.value,
      end_time: endTime.value || null,
      intensity: intensity.value,
      notes: notes.value,
      pain_location: painLocation.value,
      symptoms: symptoms.value,
      triggers: triggers.value,
    };

    if (props.eventToEdit) {
      await axios.put(`/api/migraines/${props.eventToEdit.id}`, formData);
    } else {
      await axios.post('/api/migraines/', formData);
    }

    emit('migraine-logged');

    // Reset form fields
    painLocation.value = '';
    symptoms.value = [];
    intensity.value = 5;
    startTime.value = new Date().toISOString().slice(0, 16);
    endTime.value = '';
    triggers.value = [];
    notes.value = '';

  } catch (err) {
    error.value = 'Failed to save migraine. Please try again.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="card">
    <h2>{{ eventToEdit ? 'Edit Migraine' : 'Log New Migraine' }}</h2>
    <form @submit.prevent="handleSubmit">
      <!-- Form fields -->
      <div class="form-group">
        <label for="pain-location">Pain Location</label>
        <VueMultiselect
          v-model="painLocation"
          :options="painLocationOptions"
          :taggable="true"
          placeholder="Select or add a pain location"
        />
      </div>

      <div class="form-group">
        <label for="symptoms">Symptoms</label>
        <VueMultiselect
          v-model="symptoms"
          :options="symptomOptions"
          :multiple="true"
          :taggable="true"
          placeholder="Select or add symptoms"
        />
      </div>

      <div class="form-group">
        <label for="intensity">Intensity: {{ intensity }}</label>
        <input type="range" id="intensity" v-model="intensity" min="1" max="10" />
      </div>

      <div class="form-group">
        <label for="start-time">Start Time</label>
        <input type="datetime-local" id="start-time" v-model="startTime" required />
      </div>

      <div class="form-group">
        <label for="end-time">End Time (optional)</label>
        <input type="datetime-local" id="end-time" v-model="endTime" />
      </div>

      <div class="form-group">
        <label for="triggers">Suspected Triggers</label>
        <VueMultiselect
          v-model="triggers"
          :options="triggerOptions"
          :multiple="true"
          :taggable="true"
          placeholder="Select or add triggers"
        />
      </div>

      <div class="form-group">
        <label for="notes">Notes</label>
        <textarea id="notes" v-model="notes"></textarea>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Saving...' : (eventToEdit ? 'Save Changes' : 'Log Migraine') }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--heading-color);
}

input[type="text"],
input[type="datetime-local"],
textarea {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--elevation-2-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-color);
}

input[type="range"] {
  width: 100%;
}

button {
  padding: 0.75rem 1.5rem;
  background-color: var(--elevation-2-color);
  color: var(--heading-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

button:hover {
  background-color: var(--elevation-1-color);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #ff5555;
  margin-bottom: 1rem;
}
</style>
