// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    setupSelectionFeature();
    updateCartSummary();
});

// ------------------------------
// EVENT DELEGATION FOR QUANTITY BUTTONS
// ------------------------------
document.addEventListener("click", async (e) => {
    const button = e.target.closest(".qty-btn");
    if (!button) return;

    const itemId = button.dataset.id;
    const action = button.classList.contains("increase")
        ? "increase"
        : "decrease";
    console.log("Button clicked");

    await updateCart(itemId, action);
});

// ------------------------------
// UPDATE CART VIA AJAX
// ------------------------------
async function updateCart(itemId, action) {
    try {
        const response = await fetch(`/cart/update-cart/${itemId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ action })
        });

        if (!response.ok) {
            const text = await response.text();
            console.error("Server error:", text);
            return;
        }

        const data = await response.json();

        if (data.removed) {
            document.querySelector(`#qty-${itemId}`)?.closest(".cart-item")?.remove();
            checkAndShowEmptyCart();
            updateCartSummary();
            return;
        }

        const qtyEl = document.getElementById(`qty-${itemId}`);
        if (qtyEl) qtyEl.textContent = data.quantity;

        const subtotalEl = document.getElementById(`subtotal-${itemId}`);
        if (subtotalEl) {
            subtotalEl.textContent = formatCurrency(data.subtotal);
        }

        const increaseBtn = document.querySelector(`.increase[data-id="${itemId}"]`);
        if (increaseBtn) {
            increaseBtn.disabled = data.quantity >= data.stock;
        }


        const codInput = document.getElementById("payment-cod");
        if (codInput) {
            codInput.disabled = !data.all_items_eligible_for_cod;
            codInput.checked = codInput.disabled ? false : codInput.checked;
        }

        updateCartSummary();

    } catch (err) {
        console.error("Cart update failed", err);
    }
}

// ===============================
// SELECTION FEATURE
// ===============================
function setupSelectionFeature() {
    const checkboxes = document.querySelectorAll(".select-item");
    const selectAllCheckbox = document.getElementById("select-all");
    const checkoutButton = document.getElementById("checkout-button");

    checkboxes.forEach(box => box.addEventListener("change", updateCartSummary));

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            checkboxes.forEach(box => (box.checked = selectAllCheckbox.checked));
            updateCartSummary();
        });
    }

    if (checkoutButton) {
        checkoutButton.addEventListener("click", function (e) {
            const selectedItems = getSelectedItemIDs();
            const warningMessage = document.getElementById("warning-message");
            const codInput = document.getElementById("payment-cod");
            const addressInput = document.getElementById("selected_address_input");

            // Hide warning by default
            warningMessage.classList.remove("show");

            // Validate item selection
            if (selectedItems.length === 0) {
                e.preventDefault();
                if (warningMessage) {
                    warningMessage.textContent = "✋ Please select at least one item before placing the order.";
                    warningMessage.classList.add("show");
                    warningMessage.scrollIntoView({ behavior: "smooth" });
                }
                return;
            }

            // Validate address selection
            if (!addressInput || !addressInput.value) {
                e.preventDefault();
                if (warningMessage) {
                    warningMessage.textContent = "📍 Please select a delivery address before placing the order.";
                    warningMessage.classList.add("show");
                    warningMessage.scrollIntoView({ behavior: "smooth" });
                }
                return;
            }

            // Validate payment method selection
            if (!document.querySelector('input[name="payment_method"]:checked')) {
                e.preventDefault();
                if (warningMessage) {
                    warningMessage.textContent = "💳 Please select a payment method before placing the order.";
                    warningMessage.classList.add("show");
                    warningMessage.scrollIntoView({ behavior: "smooth" });
                }
                return;
            }

            // All validations passed
            placeSelectedOrder(selectedItems);
        });
    }
}

// ===============================
// UPDATE CART SUMMARY + COD LOGIC
// ===============================
function updateCartSummary() {
    const checkboxes = document.querySelectorAll(".select-item");
    const codInput = document.getElementById("payment-cod");

    let total = 0;
    let totalItems = 0;
    let allSelectedItemsCOD = true;

    checkboxes.forEach(box => {
        // CALCULATE ONLY SELECTED ITEMS
        if (box.checked) {
            const id = box.dataset.id;
            const qty = parseInt(document.getElementById(`qty-${id}`).textContent || 0);
            const subtotal = parseNumber(
                document.getElementById(`subtotal-${id}`).textContent
            );

            total += subtotal;
            totalItems += qty;

            // ❌ If ANY selected item is non-COD
            if (box.dataset.cod !== "true") {
                allSelectedItemsCOD = false;
            }
        }
    });

    // ===============================
    // COD ENABLE / DISABLE
    // ===============================
    if (totalItems === 0) {
        disableCOD("Select at least one item to enable COD");
    }
    else if (!allSelectedItemsCOD) {
        disableCOD("Some selected items are not eligible for Cash on Delivery");
    }
    else {
        enableCOD();
    }

    // ===============================
    // UPDATE SUMMARY
    // ===============================
    setSummaryDisplays(total, totalItems, total);
}

// ===============================
// COD HELPERS
// ===============================
function disableCOD(message) {
    const codInput = document.getElementById("payment-cod");
    const tooltip = document.getElementById("cod-tooltip");

    codInput.disabled = true;
    codInput.checked = false;

    if (tooltip) {
        tooltip.textContent = message;
        tooltip.classList.add("show");
    }
}

function enableCOD() {
    const codInput = document.getElementById("payment-cod");
    const tooltip = document.getElementById("cod-tooltip");

    codInput.disabled = false;
    if (tooltip) {
        tooltip.classList.remove("show");
    }

    // Auto-select COD if nothing else selected
    if (!document.querySelector('input[name="payment_method"]:checked')) {
        codInput.checked = true;
    }
}

// ===============================
// SUMMARY DISPLAY
// ===============================
function setSummaryDisplays(total, items, grand) {
    const totalDisplay = document.getElementById("total-price");
    const summaryItems = document.getElementById("total-items");
    const grandTotalEl = document.getElementById("grand-total");

    if (totalDisplay) totalDisplay.textContent = formatCurrency(total);
    if (summaryItems) summaryItems.textContent = items;
    if (grandTotalEl) grandTotalEl.textContent = formatCurrency(grand);
}

// ===============================
// UTILITIES
// ===============================
function parseNumber(value) {
    return parseFloat(value.toString().replace(/[^\d.-]/g, "")) || 0;
}

function formatCurrency(amount) {
    return `₹${Number(amount).toFixed(2)}`;
}

function getSelectedItemIDs() {
    return Array.from(document.querySelectorAll(".select-item"))
        .filter(box => box.checked)
        .map(box => box.dataset.id);
}

function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name)) return trimmed.substring(name.length);
    }
    return "";
}

function checkAndShowEmptyCart() {
    const remainingItems = document.querySelectorAll(".cart-item");

    if (remainingItems.length === 0) {

        // 1️⃣ Hide all cart layouts
        document.querySelectorAll(".cart-layout").forEach(layout => {
            layout.style.display = "none";
        });

        // 2️⃣ Show empty cart
        const emptyLayout = document.getElementById("empty-cart-layout");
        if (emptyLayout) emptyLayout.style.display = "block";

        // 3️⃣ 🔥 FORCE correct centering layout
        const mainContainer = document.querySelector(".main-cart-div");
        if (mainContainer) {
            mainContainer.classList.add("empty-cart-layout");
        }
    }
}



// -----------------------------------------------------------
// ADDRESS DROPDOWN — HANDLE OPTION CLICK + UPDATE HIDDEN INPUT
// -----------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const selectedOption = document.querySelector(".selected-option");
    const options = document.querySelectorAll(".option");
    const hiddenAddressInput = document.getElementById("selected_address_input");

    // Toggle dropdown visibility
    document.getElementById("selected_address").addEventListener("click", function () {
        this.classList.toggle("open");
    });

    // When user selects an address
    options.forEach(opt => {
        opt.addEventListener("click", function () {

            // Update visible text in the dropdown
            selectedOption.innerHTML = this.innerHTML;

            // Update hidden input value
            hiddenAddressInput.value = this.dataset.id;

            // Close dropdown
            document.getElementById("selected_address").classList.remove("open");
        });
    });
});


// ---------------------------------------------
// GET SELECTED ADDRESS FROM HIDDEN INPUT
// ---------------------------------------------
function getSelectedAddressId() {
    const addressId = document.getElementById("selected_address_input").value;
    console.log("Selected Address ID:", addressId);
    return addressId || null;
}

// -----------------------------------------------------------
// PLACE ORDER — SEND ITEMS + ADDRESS + PAYMENT METHOD
// -----------------------------------------------------------
async function placeSelectedOrder(selectedItems) {
    try {
        if (!selectedItems || selectedItems.length === 0) {
            alert("Please select at least one item");
            return;
        }

        const addressId = getSelectedAddressId();
        if (!addressId) {
            alert("Please select an address");
            return;
        }

        const paymentInput = document.querySelector(
            'input[name="payment_method"]:checked'
        );

        if (!paymentInput) {
            alert("Please select a payment method");
            return;
        }

        const response = await fetch("/orders/confirm_order/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                selected_items: selectedItems,
                selected_address: addressId,
                payment_method: paymentInput.value
            })
        });

        const data = await response.json();

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }

    } catch (err) {
        console.error("Order Error:", err);
        alert("❌ Error placing order. Try again.");
    }
}


