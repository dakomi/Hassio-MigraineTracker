<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import LogMigraineForm from './LogMigraineForm.vue';
import Settings from './Settings.vue';
import Calendar from './Calendar.vue';

const showLogForm = ref(false);
const showSettings = ref(false);
const allMigraines = ref([]);
const isLoading = ref(true);
const error = ref(null);
const eventToEdit = ref(null);

const fetchMigraines = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await axios.get('/api/migraines/');
    allMigraines.value = response.data || [];
  } catch (err) {
    error.value = 'Failed to fetch migraine data.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchMigraines);

const recentMigraine = computed(() => {
  if (allMigraines.value.length === 0) {
    return null;
  }
  return allMigraines.value.sort(
    (a, b) => new Date(b.start_time) - new Date(a.start_time)
  )[0];
});

const handleMigraineLogged = () => {
  showLogForm.value = false;
  eventToEdit.value = null;
  fetchMigraines();
};

const openEditForm = (event) => {
  eventToEdit.value = event;
  showLogForm.value = true;
  showSettings.value = false;
};

const toggleLogForm = () => {
  showLogForm.value = !showLogForm.value;
  eventToEdit.value = null; // Clear any event being edited
  showSettings.value = false; // Hide settings when logging a migraine
};

const toggleSettings = () => {
  showSettings.value = !showSettings.value;
  showLogForm.value = false; // Hide log form when showing settings
};
</script>

<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="header-buttons">
        <button @click="toggleLogForm" v-if="!showSettings">
          {{ showLogForm ? 'Cancel' : 'Log New Migraine' }}
        </button>
        <button @click="toggleSettings">
          {{ showSettings ? 'Close Settings' : 'Settings' }}
        </button>
      </div>
    </header>

    <div v-if="showLogForm">
      <LogMigraineForm :event-to-edit="eventToEdit" @migraine-logged="handleMigraineLogged" />
    </div>

    <div v-else-if="showSettings">
      <Settings />
    </div>

    <div v-else>
      <div class="card recent-migraine">
        <h2>Most Recent Migraine</h2>
        <div v-if="isLoading">
          <p>Loading...</p>
        </div>
        <div v-else-if="error">
          <p class="error">{{ error }}</p>
        </div>
        <div v-else-if="recentMigraine">
          <p><strong>Start Time:</strong> {{ new Date(recentMigraine.start_time).toLocaleString() }}</p>
          <p><strong>Intensity:</strong> {{ recentMigraine.intensity }}</p>
          <p><strong>Pain Location:</strong> {{ recentMigraine.pain_location.name }}</p>
          <p><strong>Symptoms:</strong> {{ recentMigraine.symptoms.map(s => s.name).join(', ') }}</p>
          <p><strong>Triggers:</strong> {{ recentMigraine.triggers.map(t => t.name).join(', ') }}</p>
          <p v-if="recentMigraine.notes"><strong>Notes:</strong> {{ recentMigraine.notes }}</p>

          <div class="prompts">
            <p v-if="!recentMigraine.end_time">
              This migraine is still active.
              <button class="link-button" @click="openEditForm(recentMigraine)">When did it end?</button>
            </p>
            <p v-else>
              Was this migraine start time accurate?
              <button class="link-button" @click="openEditForm(recentMigraine)">Edit if needed</button>
            </p>
          </div>
        </div>
        <div v-else>
          <p>No migraine events logged yet.</p>
        </div>
      </div>

      <div class="card calendar-view">
        <h2>Calendar</h2>
        <Calendar :events="allMigraines" @edit-event="openEditForm" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-buttons {
  display: flex;
  gap: 1rem;
}

.recent-migraine, .calendar-view {
  margin-top: 2rem;
}

.error {
  color: #ff5555;
}

.prompts {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.link-button {
  background: none;
  border: none;
  color: var(--heading-color);
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
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
</style>
