
document.addEventListener('DOMContentLoaded', function () {
  const menuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('menu-icon');
  const closeIcon = document.getElementById('close-icon');

  menuButton.addEventListener('click', function () {
    // Toggle the hidden class on the mobile menu
    mobileMenu.classList.toggle('hidden');
    
    // Toggle the visibility of the icons
    menuIcon.classList.toggle('hidden');
    closeIcon.classList.toggle('hidden');
    
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', !expanded);
  });
});