import { useEffect, useRef } from "react";
import slide1 from "@/assets/slides/slide1.jpg";
import slide2 from "@/assets/slides/slide2.png";
import slide3 from "@/assets/slides/slide3.jpeg";
import slide4 from "@/assets/slides/slide4.jpg";

const slides = [slide1, slide2, slide3, slide4];
export default function HeroSlideshow() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    let index = 0;
    const slideWidth = el.clientWidth;

    const interval = setInterval(() => {
      index = (index + 1) % slides.length;
      el.style.transform = `translateX(-${index * slideWidth}px)`;
    }, 5000); // 5s mỗi lần chuyển

    window.addEventListener(
      "resize",
      () => (el.style.transform = "translateX(0)")
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="overflow-hidden w-full relative h-[400px]">
      <div
        ref={containerRef}
        className="flex transition-transform duration-1000 ease-in-out"
      >
        {slides.map((src, i) => (
          <img
            key={i}
            src={src}
            alt={`slide-${i}`}
            className="w-full flex-shrink-0"
          />
        ))}
      </div>
    </div>
  );
}
