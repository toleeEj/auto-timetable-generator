// main.js

document.addEventListener('DOMContentLoaded', function() {
          // Initialize Bootstrap tooltips
          var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
          var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
              return new bootstrap.Tooltip(tooltipTriggerEl);
          });
      
          // Initialize Masonry for grid layout
          if (document.querySelector('.grid')) {
              var msnry = new Masonry('.grid', {
                  itemSelector: '.grid-item',
                  columnWidth: '.grid-sizer',
                  percentPosition: true,
                  gutter: 20
              });
          }
      
          // Navbar Sticky Effect - adds or removes the sticky class based on scroll position
          var navbar = document.querySelector('.navbar-custom');
          if (navbar) {
              window.addEventListener('scroll', function() {
                  if (window.scrollY > 10) {
                      navbar.classList.add('sticky');
                  } else {
                      navbar.classList.remove('sticky');
                  }
              });
          }
      
          // Scroll-to-top button functionality (optional)
          var scrollToTopBtn = document.createElement('button');
          scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
          scrollToTopBtn.classList.add('btn', 'btn-primary', 'scroll-to-top');
          document.body.appendChild(scrollToTopBtn);
      
          scrollToTopBtn.addEventListener('click', function() {
              window.scrollTo({ top: 0, behavior: 'smooth' });
          });
      
          // Show or hide the scroll-to-top button based on the scroll position
          window.addEventListener('scroll', function() {
              if (window.scrollY > 300) {
                  scrollToTopBtn.style.display = 'block';
              } else {
                  scrollToTopBtn.style.display = 'none';
              }
          });
      });
      