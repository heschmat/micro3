// "use client";

// import { useEffect, useState } from "react";
// import { useParams } from "next/navigation";

// type Video = {
//   id: string;
//   status: string;
//   output_path?: string;
//   error?: string;
// };

// export default function StatusPage() {
//   const params = useParams();
//   const id = params.id as string;

//   const [video, setVideo] = useState<Video | null>(null);

//   useEffect(() => {
//     const interval = setInterval(async () => {
//       const res = await fetch(`http://localhost:8000/videos/${id}`);
//       const data = await res.json();
//       setVideo(data);
//     }, 2000);

//     return () => clearInterval(interval);
//   }, [id]);

//   return (
//     <main className="p-10 max-w-xl mx-auto space-y-4">
//       <h1 className="text-2xl font-bold">Status</h1>

//       {!video && <p>Loading...</p>}

//       {video && (
//         <div className="space-y-2">
//           <p><strong>ID:</strong> {video.id}</p>
//           <p><strong>Status:</strong> {video.status}</p>

//           {video.error && (
//             <p className="text-red-500">Error: {video.error}</p>
//           )}

//           {video.status === "completed" && video.output_path && (
//             <a
//               href={`http://localhost:9000/audios/${video.output_path}`}
//               className="text-green-600 underline"
//             >
//               Download Audio
//             </a>
//           )}
//         </div>
//       )}
//     </main>
//   );
// }

"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

type Video = {
  id: string;
  status: string;
  output_path?: string | null;
  error?: string | null;
  input_path?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DOWNLOAD_BASE_URL =
  process.env.NEXT_PUBLIC_DOWNLOAD_BASE_URL || "http://localhost:9000/audios";

function getStatusMeta(status: string) {
  switch (status) {
    case "uploaded":
      return {
        label: "Queued",
        progress: 25,
        badge: "bg-blue-100 text-blue-700 border-blue-200",
        bar: "w-1/4",
        description: "Your file was uploaded successfully and is waiting to be processed.",
      };
    case "processing":
      return {
        label: "Processing",
        progress: 65,
        badge: "bg-amber-100 text-amber-700 border-amber-200",
        bar: "w-2/3",
        description: "The converter service is extracting audio from your video now.",
      };
    case "completed":
      return {
        label: "Completed",
        progress: 100,
        badge: "bg-emerald-100 text-emerald-700 border-emerald-200",
        bar: "w-full",
        description: "Your MP3 is ready to download.",
      };
    case "failed":
      return {
        label: "Failed",
        progress: 100,
        badge: "bg-red-100 text-red-700 border-red-200",
        bar: "w-full",
        description: "The job failed during processing.",
      };
    default:
      return {
        label: status || "Unknown",
        progress: 10,
        badge: "bg-gray-100 text-gray-700 border-gray-200",
        bar: "w-[10%]",
        description: "The system is initializing this job.",
      };
  }
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function StatusPage() {
  const params = useParams();
  const id = params.id as string;

  const [video, setVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/videos/${id}`, {
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error(`Failed to fetch status (${res.status})`);
        }

        const data: Video = await res.json();

        if (cancelled) return;

        setVideo(data);
        setFetchError(null);
        setLoading(false);

        if (data.status === "completed" || data.status === "failed") {
          if (intervalId) clearInterval(intervalId);
        }
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof Error ? err.message : "Unknown error";
        setFetchError(message);
        setLoading(false);
      }
    };

    fetchStatus();
    intervalId = setInterval(fetchStatus, 2000);

    return () => {
      cancelled = true;
      if (intervalId) clearInterval(intervalId);
    };
  }, [id]);

  const statusMeta = useMemo(
    () => getStatusMeta(video?.status || "unknown"),
    [video?.status]
  );

  const downloadUrl =
    video?.output_path ? `${DOWNLOAD_BASE_URL}/${video.output_path}` : null;

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Processing Dashboard</p>
            <h1 className="text-3xl font-bold text-gray-900">Video Job Status</h1>
          </div>

          <Link
            href="/"
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
          >
            ← Back to Upload
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <section className="lg:col-span-2 rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-gray-500">Job ID</p>
                <p className="mt-1 break-all font-mono text-sm text-gray-800">
                  {id}
                </p>
              </div>

              <span
                className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${statusMeta.badge}`}
              >
                {statusMeta.label}
              </span>
            </div>

            <div className="mt-8">
              <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
                <span>Pipeline Progress</span>
                <span>{statusMeta.progress}%</span>
              </div>

              <div className="h-3 w-full rounded-full bg-gray-200 overflow-hidden">
                <div
                  className={`h-full rounded-full bg-blue-500 transition-all duration-500 ${statusMeta.bar}`}
                />
              </div>

              <p className="mt-4 text-sm text-gray-600">
                {statusMeta.description}
              </p>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Current Status
                </p>
                <p className="mt-2 text-lg font-semibold text-gray-900">
                  {video?.status || (loading ? "Loading..." : "Unknown")}
                </p>
              </div>

              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-500">
                  Output File
                </p>
                <p className="mt-2 break-all text-sm text-gray-800">
                  {video?.output_path || "Not ready yet"}
                </p>
              </div>
            </div>

            {loading && (
              <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
                Loading job status...
              </div>
            )}

            {fetchError && (
              <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                Failed to load status: {fetchError}
              </div>
            )}

            {video?.status === "failed" && (
              <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4">
                <p className="text-sm font-semibold text-red-700">Processing failed</p>
                <p className="mt-2 text-sm text-red-600">
                  {video.error || "No error details were provided."}
                </p>
              </div>
            )}

            {video?.status === "completed" && downloadUrl && (
              <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
                <p className="text-sm font-semibold text-emerald-700">
                  Audio is ready
                </p>
                <p className="mt-2 text-sm text-emerald-600">
                  Your converted MP3 has been generated successfully.
                </p>
                <a
                  href={downloadUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-flex rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                >
                  Download MP3
                </a>
              </div>
            )}
          </section>

          <aside className="space-y-6">
            <section className="rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Job Details</h2>

              <div className="mt-4 space-y-4 text-sm">
                <div>
                  <p className="text-gray-500">Input File</p>
                  <p className="mt-1 break-all text-gray-800">
                    {video?.input_path || "—"}
                  </p>
                </div>

                <div>
                  <p className="text-gray-500">Created At</p>
                  <p className="mt-1 text-gray-800">
                    {formatDate(video?.created_at)}
                  </p>
                </div>

                <div>
                  <p className="text-gray-500">Last Updated</p>
                  <p className="mt-1 text-gray-800">
                    {formatDate(video?.updated_at)}
                  </p>
                </div>
              </div>
            </section>

            <section className="rounded-2xl bg-white p-6 shadow-sm border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Pipeline Stages</h2>

              <div className="mt-4 space-y-3">
                <Stage
                  title="Uploaded"
                  active={
                    video?.status === "uploaded" ||
                    video?.status === "processing" ||
                    video?.status === "completed"
                  }
                />
                <Stage
                  title="Processing"
                  active={
                    video?.status === "processing" ||
                    video?.status === "completed"
                  }
                />
                <Stage
                  title="Completed"
                  active={video?.status === "completed"}
                />
              </div>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}

function Stage({
  title,
  active,
}: {
  title: string;
  active: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-3 rounded-xl border p-3 ${
        active
          ? "border-blue-200 bg-blue-50"
          : "border-gray-200 bg-gray-50"
      }`}
    >
      <div
        className={`h-3 w-3 rounded-full ${
          active ? "bg-blue-500" : "bg-gray-300"
        }`}
      />
      <span
        className={`text-sm font-medium ${
          active ? "text-blue-700" : "text-gray-600"
        }`}
      >
        {title}
      </span>
    </div>
  );
}
