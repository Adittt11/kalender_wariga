import ChatWariga from "../components/ChatWariga";

export default function TanyaWarigaAI() {
  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-2xl font-bold">Tanya Wariga AI</h1>
        <p className="mt-3 text-sm leading-7 text-gray-500">
          Halaman ini digunakan untuk bertanya seputar kalender Bali, dewasa ayu,
          pakakalan, karakter kelahiran, dan informasi Wariga lainnya.
        </p>
      </section>
      <ChatWariga />
    </div>
  );
}
