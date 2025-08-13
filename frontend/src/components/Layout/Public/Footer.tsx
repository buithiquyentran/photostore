const Footer = () => {
  return (
    <section className="bg-headline text-main py-12 text-center px-8 flex">
      <div>
        <h3 className="text-3xl font-semibold mb-4">
          Subscribe to our newsletter
        </h3>
        <p className="max-w-lg mx-auto text-main/80 mb-6">
          Get the latest photo tips, platform updates, and exclusive offers
          delivered straight to your inbox.
        </p>
      </div>
      <div className="max-w-md mx-auto">
        <input
          type="email"
          placeholder="Your email address"
          className="w-full p-3 mb-4 rounded-lg border border-main focus:outline-none focus:ring-2 focus:ring-main"
        />
        <button className="w-full bg-tertiary text-headline p-3 rounded-lg hover:opacity-90 transition">
          Subscribe
        </button>
        <p className="text-sm text-main/60 mt-4 max-w-sm mx-auto">
          We respect your privacy. You can unsubscribe at any time. Read our{" "}
          <a href="/privacy" className="underline hover:text-tertiary">
            Privacy Policy
          </a>
          .
        </p>
      </div>
    </section>
  );
};
export default Footer;
