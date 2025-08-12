import { Search, Camera } from "lucide-react";
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
  return (
    <div className=" min-h-screen">
      <nav className="bg-headline text-white px-6 py-3 flex items-center justify-between">
        <div className="flex items-center justify-center gap-2 underline underline-offset-4 decoration-4 decoration-highlight">
          <div>
            <Camera className="w-10 h-10 text-tertiary" />
          </div>
          <span className="font-semibold text-2xl text-tertiary">
            photostore
          </span>
        </div>

        {/* Menu trái */}
        <ul className="flex items-center space-x-6 text-sm font-medium">
          <li className="hover:text-highlight cursor-pointer">Platform</li>
          <li className="hover:text-highlight cursor-pointer">Solutions</li>
          <li className="hover:text-highlight cursor-pointer">Developers</li>
          <li className="hover:text-highlight cursor-pointer">Resources</li>
          <li className="hover:text-highlight cursor-pointer">About Us</li>
          <li className="hover:text-highlight cursor-pointer">Pricing</li>
        </ul>

        {/* Menu phải */}
        <ul className="flex items-center space-x-4 text-sm font-medium">
          <li>
            <Search className="w-4 h-4 cursor-pointer hover:text-highlight" />
          </li>
          <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
            Contact
          </li>
          <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
            Support
          </li>
          <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
            Documentation
          </li>
          <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
            Login
          </li>
        </ul>
      </nav>
      <header className="hero-section py-16 text-center text-headline relative overflow-hidden">
        <div className="absolute inset-0 animate-gradient bg-gradient"></div>
        <div className="relative z-10">
          <h1 className="text-5xl font-bold text-headline mb-4">PHOTOSTORE</h1>
          <p className="text-lg max-w-xl mx-auto">
            Browse Your Life in Pictures - Safe, Organized, and Always with You.
          </p>
          <button className="mt-8 bg-highlight text-paragraph px-6 py-3 rounded-lg hover:bg-highlight">
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

      <section className="bg-headline text-main py-12 text-center px-8">
        <h3 className=" text-3xl font-semibold  mb-4">
          Subscribe to our newsletter
        </h3>

        <div className="max-w-md mx-auto">
          <input
            type="email"
            placeholder="Email của bạn"
            className="w-full p-3 mb-4 rounded-lg border border-main focus:outline-none focus:ring-2 focus:ring-main"
          />
          <button className="w-full bg-tertiary text-headline p-3 rounded-lg">
            Gửi
          </button>
        </div>
      </section>
    </div>
  );
}
export default Home;
