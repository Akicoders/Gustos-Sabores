export function createTextElement(tag: string, text: string, className?: string): HTMLElement {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

export function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/** Adds `.is-visible` to `[data-reveal]` elements as they scroll into view (or immediately if motion is reduced). */
export function revealOnScroll(selector = '[data-reveal]'): void {
  const elements = Array.from(document.querySelectorAll<HTMLElement>(selector));
  if (!elements.length) return;

  if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
    elements.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
  );

  elements.forEach((el) => observer.observe(el));
}

/** Briefly pulses an element to acknowledge an action (skips when motion is reduced). */
export function pulse(element: Element | null): void {
  if (!element || prefersReducedMotion()) return;
  element.classList.remove('is-pulsing');
  void (element as HTMLElement).offsetWidth;
  element.classList.add('is-pulsing');
}
