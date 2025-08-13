import HeroSlideshow from "./slideshow";
import path from "@/resources/path";
import { useNavigate } from "react-router-dom";
const features = [
  {
    title: "Upload & Storage",
    description:
      "Easily upload images and videos from your device, URLs, or direct integrations.",
  },
  {
    title: "Automatic Optimization",
    description:
      "Compress and deliver media in modern formats like WebP and AVIF without quality loss.",
  },
  {
    title: "Transformations",
    description:
      "Resize, crop, rotate, add watermarks, and apply effects on the fly.",
  },
  {
    title: "Media Library",
    description:
      "Search, filter, and organize your media assets with tags and folders.",
  },
  {
    title: "Global CDN Delivery",
    description: "Serve media quickly anywhere in the world with edge caching.",
  },
  {
    title: "Security",
    description:
      "Protect your assets with signed URLs, token authentication, and access control.",
  },
  {
    title: "Analytics",
    description:
      "Track usage, view download stats, and monitor performance in real-time.",
  },
  {
    title: "API & SDKs",
    description:
      "Integrate seamlessly into your web and mobile apps with robust APIs.",
  },
  {
    title: "AI Tagging",
    description:
      "Automatically detect objects, faces, and scenes in your images.",
  },
];
function Home() {
  const navigate = useNavigate();
  return (
    <div className=" min-h-screen">
      <header className="relative hero-section text-center text-headline overflow-hidden">
        <HeroSlideshow />
        <div className="absolute inset-0 flex flex-col justify-center items-center text-center px-4">
          <h1 className="text-5xl font-bold text-white mb-4 [text-shadow:_2px_2px_8px_rgba(0,0,0,0.7)]">
            PHOTOSTORE
          </h1>
          <p className="text-lg text-white max-w-xl [text-shadow:_2px_2px_8px_rgba(0,0,0,0.7)]">
            Browse Your Life in Pictures - Safe, Organized, and Always with You.
          </p>
          <button
            className="mt-8 bg-highlight text-paragraph px-6 py-3 rounded-lg hover:bg-highlight"
            onClick={() => navigate(path.LOGIN)}
          >
            Get started!
          </button>
        </div>
      </header>

      <section className="py-12 bg-secondary grid gap-4 md:grid-cols-2 lg:grid-cols-3 px-8">
        {features.map((feature, index) => (
          <div
            key={index}
            className="bg-main rounded-lg shadow-lg p-6 hover:shadow-xl transition"
          >
            <h2 className="text-2xl font-semibold text-headline mb-2">
              {feature.title}
            </h2>
            <p className="text-paragraph">{feature.description}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
export default Home;
