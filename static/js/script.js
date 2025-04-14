let menuOpen = false;

function toggleMenu(event) {
  const menu = document.getElementById("menu");
  const navToggle = document.querySelector(".nav-toggle");

  // Toggle the menu visibility
  menuOpen = !menuOpen;

  // Apply a smooth sliding effect for menu
  menu.style.transition = "transform 0.3s ease-in-out"; // Add transition for smooth animation
  menu.style.transform = menuOpen ? "translateX(0)" : "translateX(-100%)";

  // Prevent menu from closing immediately when the button is clicked
  event.stopPropagation();
}

// Close menu when clicking anywhere outside it
document.addEventListener("click", function (event) {
  const menu = document.getElementById("menu");
  const toggleBtn = document.querySelector(".nav-toggle");

  if (
    menuOpen &&
    !menu.contains(event.target) &&
    !toggleBtn.contains(event.target)
  ) {
    // Smoothly close the menu
    menu.style.transition = "transform 0.3s ease-in-out";
    menu.style.transform = "translateX(-100%)";
    menuOpen = false;
  }
});
