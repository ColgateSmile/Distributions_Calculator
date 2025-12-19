document.addEventListener('DOMContentLoaded', function () {
  const cards = document.querySelectorAll('.dist-card');

  cards.forEach(card => {
    card.addEventListener('click', function (e) {
      // Don't toggle when clicking on links or buttons
      if (e.target.closest('a, button')) return;
      card.classList.toggle('open');
    });
  });
});
