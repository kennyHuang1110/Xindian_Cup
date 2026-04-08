const scrollButton = document.querySelector("[data-scroll-top]");

if (scrollButton) {
    const toggleScrollButton = () => {
        scrollButton.classList.toggle("is-visible", window.scrollY > 280);
    };

    toggleScrollButton();
    window.addEventListener("scroll", toggleScrollButton, { passive: true });
    scrollButton.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}
