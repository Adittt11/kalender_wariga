import ChatWariga from "../components/ChatWariga";

export default function TanyaWarigaAI() {
  return (
    <div className="min-h-[calc(100vh-120px)] rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <div className="space-y-5 md:space-y-6">
        <section className="card p-5 sm:p-6 md:p-8">
          <h1 className="text-xl font-bold sm:text-2xl">Tanya Wariga AI</h1>
          <p className="mt-3 text-sm leading-7 text-gray-500">
            Halaman ini digunakan untuk bertanya seputar kalender Bali, dewasa ayu,
            pakakalan, karakter kelahiran, dan informasi Wariga lainnya.
          </p>
        </section>

        <ChatWariga />
      </div>
    </div>
  );
}