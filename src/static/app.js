document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function renderActivities(activities) {
    activitiesList.innerHTML = "";
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;
      const participantItems = (details.participants || [])
        .map(
          (email) => `
            <div class="participant-item">
              <span class="participant-email">${email}</span>
              <button
                type="button"
                class="participant-remove"
                data-activity="${name}"
                data-email="${email}"
                aria-label="Remove ${email}"
              >
                🗑
              </button>
            </div>
          `
        )
        .join("");
      const participantsMarkup = participantItems
        ? `<div class="participants-list">${participantItems}</div>`
        : `<p class="participants-empty">No participants yet.</p>`;

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <p class="participants-title"><strong>Participants</strong></p>
          ${participantsMarkup}
        </div>
      `;

      activitiesList.appendChild(activityCard);

      activityCard.querySelectorAll(".participant-remove").forEach((button) => {
        button.addEventListener("click", async () => {
          const activityName = button.dataset.activity;
          const participantEmail = button.dataset.email;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(participantEmail)}`,
              {
                method: "DELETE",
              }
            );
            const result = await response.json();

            if (response.ok) {
              showMessage(result.message, "success");
              await fetchActivities();
            } else {
              showMessage(result.detail || "An error occurred", "error");
            }
          } catch (error) {
            showMessage("Failed to remove participant. Please try again.", "error");
            console.error("Error removing participant:", error);
          }
        });
      });

      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      renderActivities(activities);
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
