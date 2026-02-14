const navbar = document.getElementById('mainNavbar');

if (navbar) {
	const toggleNavbarScrolled = () => {
		if (window.scrollY > 10) {
			navbar.classList.add('navbar-scrolled');
		} else {
			navbar.classList.remove('navbar-scrolled');
		}
	};

	toggleNavbarScrolled();
	window.addEventListener('scroll', toggleNavbarScrolled, { passive: true });
}