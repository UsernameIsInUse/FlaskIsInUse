console.log("Sanity check!");

fetch("/api/v1/subscriptions/config")
.then((result) => { return result.json(); })
.then((data) => {
  const stripe = Stripe(data.publicKey);
  // Event handler
  document.querySelectorAll(".monthly").forEach(button => {
    button.addEventListener("click", () => {
      // Get Checkout Session ID
      fetch("/api/v1/subscriptions/create-checkout-session/monthly")
      .then((result) => { return result.json(); })
      .then((data) => {
        console.log(data);
        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({sessionId: data.sessionId})
      })
      .then((res) => {
        console.log(res);
      });
    });
  });
  document.querySelectorAll(".yearly").forEach(button => {
    button.addEventListener("click", () => {
      // Get Checkout Session ID
      fetch("/api/v1/subscriptions/create-checkout-session/yearly")
      .then((result) => { return result.json(); })
      .then((data) => {
        console.log(data);
        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({sessionId: data.sessionId})
      })
      .then((res) => {
        console.log(res);
      });
    });
  });
  document.querySelectorAll(".portal").forEach(button => {
    button.addEventListener("click", () => {
      fetch("/api/v1/subscriptions/create-portal-session")
      .then((result) => result.json())
      .then((data) => {
        if (data.url) {
          window.location.href = data.url;  // Redirect to the portal session
        } else {
          console.error("Error:", data.error);
        }
      });
    });
  });
});