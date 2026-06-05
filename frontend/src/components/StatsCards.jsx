export default function StatsCards({
  result,
}) {
  return (
    <div className="grid grid-cols-3 gap-5 mb-8">
      <div className="bg-white p-5 rounded-xl border">
        <h3 className="text-gray-500">
          PDF Type
        </h3>

        <p className="text-2xl font-bold">
          {result.pdf_type}
        </p>
      </div>

      <div className="bg-white p-5 rounded-xl border">
        <h3 className="text-gray-500">
          Fields Found
        </h3>

        <p className="text-2xl font-bold">
          {result.total_fields_found}
        </p>
      </div>

      <div className="bg-white p-5 rounded-xl border">
        <h3 className="text-gray-500">
          Regex Fields
        </h3>

        <p className="text-2xl font-bold">
          {
            result.extraction_layers
              .regex_fields_found
          }
        </p>
      </div>
    </div>
  );
}