document.addEventListener("DOMContentLoaded", () => {
  loadAlerts(); // initial load

  const form = document.querySelector("#entryForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      try {
        const res = await fetch(form.action, {
          method: "POST",
          body: formData
        });
        if (res.ok) {
          loadAlerts(); // refresh alerts immediately after entry
        }
      } catch (err) {
        console.error("Error submitting entry:", err);
      }
    });
  }
});
