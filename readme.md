# Migraine Tracker Home Assistant Add-on

A comprehensive migraine tracking system with weather correlation capabilities, designed to be a production-ready and well-documented Home Assistant add-on.

## Features

- **Light-Sensitivity Friendly UI**: A dark, low-contrast user interface designed to be comfortable for users experiencing migraines.
- **Migraine Logging**: Easily log and edit migraine events with details such as pain location, symptoms, intensity, start/end times, and suspected triggers.
- **Weather Correlation**: Automatically fetches and stores weather data for each migraine event, helping to identify potential weather-related triggers.
- **Home Assistant Integration**: Exposes a `sensor.migraine_current_status` entity to Home Assistant, allowing you to create automations based on your migraine status.
- **Data Import/Export**: Easily back up and restore your migraine data in JSON and CSV formats.
- **Calendar View**: A monthly calendar view to visualize your migraine history at a glance.

## Installation

1.  **Add the repository to your Home Assistant instance.**
    - Go to **Settings > Add-ons > Add-on Store**.
    - Click the three dots in the top right corner and select **Repositories**.
    - Add the URL to this repository and click **Add**.

2.  **Install the Migraine Tracker add-on.**
    - The add-on will now be available in the Add-on Store.
    - Click **Install** and wait for the installation to complete.

3.  **Configure the add-on.**
    - Before starting the add-on, go to the **Configuration** tab and set your preferences.

4.  **Start the add-on.**
    - Go to the **Info** tab and click **Start**.
    - The add-on will now be running and accessible from the sidebar.

## Performance Optimization

The Migraine Tracker add-on is designed to be lightweight and performant, even on resource-constrained devices like the Raspberry Pi. However, there are a few things you can do to optimize its performance:

-   **Limit the number of migraines displayed on the calendar.** If you have a very large number of migraine events, the calendar view may become slow to load. You can limit the number of events displayed by adjusting the `calendar_event_limit` option in the configuration.
-   **Disable unused weather providers.** If you are not using the Tomorrow.io or Google Weather APIs, you can disable them in the settings to prevent unnecessary API calls.
-   **Choose a longer backup interval.** If you do not need daily backups, you can choose a weekly or monthly interval to reduce the load on your system.

## Hardware Optimization Guide for Raspberry Pi

The Migraine Tracker add-on is optimized for the Raspberry Pi 4B, but it should run well on other Raspberry Pi models as well. Here are a few tips for optimizing the performance of the add-on on a Raspberry Pi:

-   **Use a high-quality SD card.** A fast SD card will significantly improve the performance of the add-on, especially when it comes to database operations.
-   **Use a dedicated power supply.** The Raspberry Pi can be sensitive to power fluctuations, so it's important to use a high-quality power supply that can provide a stable voltage.
-   **Keep your Raspberry Pi cool.** The Raspberry Pi can throttle its performance if it gets too hot, so it's important to keep it in a well-ventilated area and consider using a heatsink or fan.
-   **Don't run too many other add-ons.** The Raspberry Pi has limited resources, so it's important to be mindful of how many other add-ons you are running. If you are experiencing performance issues, try disabling some of your other add-ons to see if that helps.

## Development

### Running Tests

**Backend (pytest)**

To run the backend tests, you will need to have `pytest` installed and all the project dependencies available in your Python environment.

1.  **Install Dependencies:**
    ```bash
    pip install -r migraine_tracker/requirements.txt
    ```

2.  **Run Tests:**
    From the root of the `migraine_tracker` directory, run the following command:
    ```bash
    TEST_ENV=true python3 -m pytest
    ```
    The `TEST_ENV=true` environment variable is necessary to ensure that the tests use a temporary directory for the encryption key.

**Frontend (vitest)**

To run the frontend tests, you will need to have `vitest` and `jsdom` installed.

1.  **Install Dependencies:**
    ```bash
    cd migraine_tracker/frontend
    npm install -D vitest jsdom @vitejs/plugin-vue @vue/test-utils
    ```

2.  **Run Tests:**
    From the `migraine_tracker/frontend` directory, run the following command:
    ```bash
    npm test
    ```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
