
const searchInput = document.querySelector("#search-input");
const filterButtons = document.querySelectorAll(".filter");
const eventCards = document.querySelectorAll(".event-card");
const eventCount = document.querySelector("#event-count");
const emptyState = document.querySelector("#empty-state");

const dialog = document.querySelector("#booking-dialog");
const bookingForm = document.querySelector("#booking-form");
const bookingTitle = document.querySelector("#booking-title");
const quantityInput = document.querySelector("#ticket-quantity");
const bookingTotal = document.querySelector("#booking-total");
const bookingMessage = document.querySelector("#booking-message");

let activeCategory = "All";
let selectedEvent = null;

function filterEvents() {
  const searchTerm = searchInput.value.trim().toLowerCase();
  let visibleCount = 0;

  eventCards.forEach((card) => {
    const matchesName = card.dataset.name.includes(searchTerm);
    const matchesCategory =
      activeCategory === "All" ||
      card.dataset.category === activeCategory;

    const visible = matchesName && matchesCategory;
    card.hidden = !visible;

    if (visible) visibleCount++;
  });

  eventCount.textContent =
    `${String(visibleCount).padStart(2, "0")} EXPERIENCES`;

  emptyState.hidden = visibleCount !== 0;
}

searchInput.addEventListener("input", filterEvents);

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeCategory = button.dataset.category;

    filterButtons.forEach((item) => {
      item.classList.toggle("active", item === button);
    });

    filterEvents();
  });
});

document.querySelectorAll(".heart-btn").forEach((button) => {
  button.addEventListener("click", () => {
    const saved = button.classList.toggle("saved");
    button.textContent = saved ? "♥" : "♡";
    button.setAttribute("aria-pressed", String(saved));
  });
});

function updateTotal() {
  if (!selectedEvent) return;

  const quantity = Number(quantityInput.value) || 1;

  bookingTotal.textContent =
    `₹${(selectedEvent.price * quantity).toLocaleString("en-IN")}`;
}

document.querySelectorAll(".book-btn").forEach((button) => {
  button.addEventListener("click", () => {
    selectedEvent = {
      id: Number(button.dataset.id),
      name: button.dataset.name,
      price: Number(button.dataset.price),
      available: Number(button.dataset.available)
    };

    bookingTitle.textContent = selectedEvent.name;
    quantityInput.value = "1";
    quantityInput.max = String(
      Math.min(6, selectedEvent.available)
    );
    bookingMessage.textContent = "";

    updateTotal();
    dialog.showModal();
  });
});

quantityInput.addEventListener("input", updateTotal);

document.querySelector("#close-dialog").addEventListener("click", () => {
  dialog.close();
});

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

bookingForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!selectedEvent) return;

  const formData = new FormData(bookingForm);
  const quantity = Number(formData.get("quantity"));

  if (
    !Number.isInteger(quantity) ||
    quantity < 1 ||
    quantity > Math.min(6, selectedEvent.available)
  ) {
    bookingMessage.textContent = "Please select a valid ticket quantity.";
    return;
  }

  const customerName = String(
    formData.get("customer_name") || ""
  ).trim();

  const customerEmail = String(
    formData.get("customer_email") || ""
  ).trim();

  if (!customerName || !customerEmail) {
    bookingMessage.textContent = "Please enter your name and email.";
    return;
  }

  const submitButton = bookingForm.querySelector(".submit-btn");

  submitButton.disabled = true;
  bookingMessage.textContent = "Sending booking request...";

  try {
    const response = await fetch("/api/book", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        event_id: selectedEvent.id,
        customer_name: customerName,
        customer_email: customerEmail,
        quantity: quantity
      })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Booking request failed.");
    }

    bookingMessage.textContent =
      `Booking request sent successfully! Booking ID: ${result.booking_id}`;

    bookingForm.reset();
  } catch (error) {
    bookingMessage.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

