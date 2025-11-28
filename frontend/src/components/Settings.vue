<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const exportStatus = ref('');
const importStatus = ref('');
const importFile = ref(null);
const settings = ref({
  tomorrow_io_api_key: '',
  google_weather_api_key: '',
  indoor_temp_sensor: null,
  indoor_humidity_sensor: null,
  fetch_frequency: '1h',
  fetch_range_before: 3,
  fetch_range_after: 1,
  backup_interval: 'daily',
});
const saveStatus = ref('');
const haEntities = ref([]);
const lastBackup = ref('N/A');

const fetchSettings = async () => {
  try {
    const response = await axios.get('/api/settings/');
    settings.value = response.data;
  } catch (error) {
    console.error('Failed to fetch settings:', error);
  }
};

const fetchHaEntities = async () => {
  try {
    const response = await axios.get('/api/ha_entities/');
    haEntities.value = response.data;
  } catch (error) {
    console.error('Failed to fetch Home Assistant entities:', error);
  }
};

// TODO: Implement a way to get the last backup status
const fetchLastBackup = async () => {};

onMounted(() => {
  fetchSettings();
  fetchHaEntities();
  fetchLastBackup();
});

const sensorEntities = computed(() => {
  return haEntities.value
    .filter(e => e.entity_id.startsWith('sensor.'))
    .map(e => e.entity_id);
});

const handleSaveSettings = async () => {
  saveStatus.value = 'Saving...';
  try {
    await axios.post('/api/settings/', settings.value);
    saveStatus.value = 'Settings saved successfully!';
  } catch (error) {
    saveStatus.value = 'Failed to save settings.';
    console.error('Failed to save settings:', error);
  }
};

const handleExport = async (type) => {
  exportStatus.value = 'Exporting...';
  try {
    let url, filename;
    if (type === 'csv') {
      url = '/api/export/csv';
      filename = 'migraine_data.csv';
    } else if (type === 'json') {
      url = '/api/export/';
      filename = 'migraine_data.json';
    } else if (type === 'preferences') {
      url = '/api/preferences/export';
      filename = 'migraine_preferences.json';
    }

    const response = await axios.get(url, { responseType: 'blob' });
    const fileUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = fileUrl;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    exportStatus.value = 'Export successful!';
  } catch (error) {
    exportStatus.value = 'Export failed.';
    console.error('Export error:', error);
  }
};

const handleFileChange = (event) => {
  importFile.value = event.target.files[0];
};

const handleImport = async (type) => {
  if (!importFile.value) {
    importStatus.value = 'Please select a file to import.';
    return;
  }

  importStatus.value = 'Importing... This may take a while if weather data needs to be fetched.';
  const formData = new FormData();
  formData.append('file', importFile.value);

  const url = type === 'preferences' ? '/api/preferences/import' : '/api/import/';

  try {
    await axios.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    importStatus.value = 'Import successful!';
  } catch (error) {
    importStatus.value = 'Import failed.';
    console.error('Import error:', error);
  }
};
</script>

<template>
  <div class="settings-panel card">
    <h2>Settings</h2>

    <div class="settings-section">
      <h3>Weather API Configuration</h3>
      <!-- ... existing weather settings ... -->
    </div>

    <div class="settings-section">
      <h3>Data Management</h3>
      <div class="data-management">
        <div class="export-section">
          <h4>Export</h4>
          <button @click="handleExport('json')">Export Data (JSON)</button>
          <button @click="handleExport('csv')">Export Data (CSV)</button>
          <button @click="handleExport('preferences')">Export Preferences</button>
          <p v-if="exportStatus">{{ exportStatus }}</p>
        </div>
        <div class="import-section">
          <h4>Import</h4>
          <input type="file" @change="handleFileChange" accept=".json" />
          <button @click="handleImport('data')">Import Data</button>
          <button @click="handleImport('preferences')">Import Preferences</button>
          <p class="warning">
            Note: Importing a large number of events may take a long time as
            historical weather data is fetched for each event.
          </p>
          <p v-if="importStatus">{{ importStatus }}</p>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <h3>Automatic Backups</h3>
      <div class="form-group">
        <label for="backup-interval">Backup Interval</label>
        <select id="backup-interval" v-model="settings.backup_interval">
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="never">Never</option>
        </select>
      </div>
      <p>Last Backup: {{ lastBackup }}</p>
      <button @click="handleSaveSettings">Save Settings</button>
      <p v-if="saveStatus">{{ saveStatus }}</p>
    </div>
  </div>
</template>

<style scoped>
/* ... existing styles ... */
</style>
