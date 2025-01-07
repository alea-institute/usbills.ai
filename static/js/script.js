// Mobile menu toggle
const mobileMenuButton = document.querySelector('[aria-controls="mobile-menu"]');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuButton.addEventListener('click', () => {
    const expanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
    mobileMenuButton.setAttribute('aria-expanded', !expanded);
    mobileMenu.classList.toggle('hidden');
});

function updatePercentileColor() {
    const elements = document.querySelectorAll('.percentile-color');

    elements.forEach(element => {
        const percentile = parseFloat(element.dataset.percentile);

        if (isNaN(percentile)) {
            console.error("Element with class 'percentile-color' is missing or has an invalid data-percentile attribute:", element);
            return;
        }

        const percentage = Math.max(0, Math.min(100, percentile));
        const isInverted = element.dataset.inverted === "true";

        let red, green, blue;

        // Define the target mid-gray color
        const midGray = 128;

        // Define how much gray to mix (0.0 = no gray, 1.0 = fully gray)
        const grayMixFactor = 0.4;

        if (!isInverted) { // Green to Red mixed with Gray
            if (percentage < 50) {
                // Transition from Green towards mid-gray
                green = 255;
                red = Math.round(2 * percentage);
                blue = 0;
            } else {
                // Transition from mid-gray to Red
                red = 255;
                green = Math.round(2 * (100 - percentage));
                blue = 0;
            }
        } else { // Red to Green mixed with Gray (Inverted)
            if (percentage < 50) {
                red = 255;
                green = Math.round(2 * percentage);
                blue = 0;
            } else {
                green = 255;
                red = Math.round(2 * (100 - percentage));
                blue = 0;
            }
        }

        // Mix the calculated color with gray
        red = Math.round(red * (1 - grayMixFactor) + midGray * grayMixFactor);
        green = Math.round(green * (1 - grayMixFactor) + midGray * grayMixFactor);
        blue = Math.round(blue * (1 - grayMixFactor) + midGray * grayMixFactor);

        const textColor = `rgb(${red},${green},${blue})`;
        element.style.color = textColor;
    });
}

updatePercentileColor();