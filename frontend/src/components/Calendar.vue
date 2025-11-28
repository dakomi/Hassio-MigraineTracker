<script setup>
import { ref, computed } from 'vue';
import EventModal from './EventModal.vue';

const props = defineProps({
  events: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['edit-event']);

const currentDate = ref(new Date());
const selectedEvent = ref(null);
const showModal = ref(false);

const monthNames = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const currentMonth = computed(() => monthNames[currentDate.value.getMonth()]);
const currentYear = computed(() => currentDate.value.getFullYear());

const daysInMonth = computed(() => {
  const year = currentYear.value;
  const month = currentDate.value.getMonth();
  const date = new Date(year, month, 1);
  const days = [];

  // Get the first day of the month
  const firstDay = new Date(year, month, 1).getDay();

  // Add blank days for the first week
  for (let i = 0; i < firstDay; i++) {
    days.push({ date: '' });
  }

  // Add the days of the month
  while (date.getMonth() === month) {
    const dayDate = new Date(date);
    const dayEvents = props.events.filter(event =>
      new Date(event.start_time).toDateString() === dayDate.toDateString()
    );
    days.push({ date: dayDate, events: dayEvents });
    date.setDate(date.getDate() + 1);
  }

  return days;
});

const getIntensityColor = (intensity) => {
  // Simple color scale from green to red
  const hue = 120 - (intensity * 12);
  return `hsl(${hue}, 100%, 50%)`;
};

const openModal = (event) => {
  selectedEvent.value = event;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedEvent.value = null;
};

const handleEdit = (event) => {
  closeModal();
  emit('edit-event', event);
};

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1));
};

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1));
};
</script>

<template>
  <div class="calendar">
    <div class="calendar-header">
      <button @click="prevMonth">&lt;</button>
      <h2>{{ currentMonth }} {{ currentYear }}</h2>
      <button @click="nextMonth">&gt;</button>
    </div>
    <div class="calendar-grid">
      <div class="day-name" v-for="day in daysOfWeek" :key="day">{{ day }}</div>
      <div
        class="day"
        v-for="(day, index) in daysInMonth"
        :key="index"
        @click="day.events && day.events.length > 0 ? openModal(day.events[0]) : null"
        :class="{ 'has-event': day.events && day.events.length > 0 }"
      >
        <span v-if="day.date">{{ day.date.getDate() }}</span>
        <div class="events" v-if="day.events && day.events.length > 0">
          <div
            class="event-dot"
            :style="{ backgroundColor: getIntensityColor(day.events[0].intensity) }">
          </div>
        </div>
      </div>
    </div>
    <EventModal v-if="selectedEvent" :event="selectedEvent" :show="showModal" @close="closeModal" @edit="handleEdit" />
  </div>
</template>

<style scoped>
.calendar {
  width: 100%;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.day-name, .day {
  text-align: center;
  padding: 0.5rem;
}

.day {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  min-height: 5rem;
  position: relative;
}

.day.has-event {
  cursor: pointer;
}

.event-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
}
</style>
