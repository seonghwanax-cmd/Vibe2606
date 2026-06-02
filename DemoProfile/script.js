const contactForm = document.getElementById('contact-form');

contactForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  const formData = new FormData(contactForm);
  const name = formData.get('name');
  const email = formData.get('email');
  const message = formData.get('message');

  if (name && email && message) {
    alert(`감사합니다, ${name}님!\n문의가 접수되었습니다. 빠르게 답변 드리겠습니다.`);
    contactForm.reset();
  }
});

const navMenu = document.querySelector('.nav-menu');
const menuToggle = document.querySelector('.menu-toggle');

menuToggle?.addEventListener('click', () => {
  navMenu?.classList.toggle('nav-open');
});
