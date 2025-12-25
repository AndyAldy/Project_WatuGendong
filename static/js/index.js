document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Navbar Scroll Effect (Cuma aktif di Homepage yang navbar-nya transparan)
    const navbar = document.getElementById('mainNav');
    const brand = navbar.querySelector('.navbar-brand');
    
    if(navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
                if(brand) {
                    brand.classList.remove('text-white');
                    brand.classList.add('text-dark');
                }
            } else {
                navbar.classList.remove('navbar-scrolled');
                if(brand) {
                    brand.classList.remove('text-dark');
                    brand.classList.add('text-white');
                }
            }
        });
    }

    // 2. Floating Menu Auto-Hide
    const floatMenu = document.getElementById('floatingMenu');
    let isScrolling;

    if(floatMenu) {
        window.addEventListener('scroll', () => {
            floatMenu.classList.add('hidden-nav');
            window.clearTimeout(isScrolling);
            isScrolling = setTimeout(() => {
                floatMenu.classList.remove('hidden-nav');
            }, 1000); // Muncul lagi setelah 1 detik diam
        });
    }
});