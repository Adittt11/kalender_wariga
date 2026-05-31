export default function SmallCard({ icon, title, children }) {
  return (
    <section className="card min-h-[165px] p-5">
      <div className="mb-4 flex items-center gap-4">
        <div className="rounded-full bg-baliCream p-3 text-baliBrown">
          {icon}
        </div>
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      <div className="text-sm leading-relaxed text-baliDark">{children}</div>
    </section>
  );
}
