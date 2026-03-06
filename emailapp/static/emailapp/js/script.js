document.addEventListener("DOMContentLoaded", () => {
  // ===== Mobile Menu =====
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  const closeMenuBtn = document.querySelector('.close-menu');

  if (menuToggle && mobileMenu && closeMenuBtn) {
    menuToggle.addEventListener('click', () => mobileMenu.classList.add('active'));
    closeMenuBtn.addEventListener('click', () => mobileMenu.classList.remove('active'));
    mobileMenu.addEventListener('click', (e) => {
      if (e.target === mobileMenu) mobileMenu.classList.remove('active');
    });
  }
});