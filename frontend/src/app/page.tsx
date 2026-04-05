// // "use client";

// // import { useState } from "react";

// // export default function Home() {
// //   const [file, setFile] = useState<File | null>(null);
// //   const [loading, setLoading] = useState(false);
// //   const [videoId, setVideoId] = useState<string | null>(null);

// //   const handleUpload = async () => {
// //     console.log("CLICKED"); // 👈 add this

// //     if (!file) {
// //       alert("Select a file first");
// //       return;
// //     }

// //     try {
// //       setLoading(true);

// //       const formData = new FormData();
// //       formData.append("file", file);

// //       const res = await fetch("http://localhost:8000/upload", {
// //         method: "POST",
// //         body: formData,
// //       });

// //       const data = await res.json();
// //       console.log(data);

// //       setVideoId(data.video_id);
// //     } catch (err) {
// //       console.error(err);
// //       alert("Upload failed");
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   return (
// //     <main className="p-10 max-w-xl mx-auto space-y-4">
// //       <h1 className="text-2xl font-bold">Upload Video</h1>

// //       <input
// //         type="file"
// //         onChange={(e) => setFile(e.target.files?.[0] || null)}
// //       />

// //       <button
// //         onClick={handleUpload}
// //         className="bg-blue-500 text-white px-4 py-2 rounded"
// //       >
// //         Upload
// //       </button>
// //     </main>
// //   );
// // }

// "use client";

// import { useState } from "react";

// export default function Home() {
//   const [file, setFile] = useState<File | null>(null);
//   const [loading, setLoading] = useState(false);
//   const [videoId, setVideoId] = useState<string | null>(null);

//   const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

//   const handleUpload = async () => {
//     if (!file) {
//       alert("Select a file first");
//       return;
//     }

//     try {
//       setLoading(true);

//       const formData = new FormData();
//       formData.append("file", file);

//       const res = await fetch(`${API_URL}/upload`, {
//         method: "POST",
//         body: formData,
//       });

//       const data = await res.json();
//       setVideoId(data.video_id);
//     } catch (err) {
//       console.error(err);
//       alert("Upload failed");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <main className="min-h-screen flex items-center justify-center bg-gray-100">
//       <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-md space-y-6">
//         <h1 className="text-2xl font-bold text-center">
//           🎬 Video → MP3
//         </h1>

//         <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:border-blue-400 transition">
//           <input
//             type="file"
//             className="hidden"
//             onChange={(e) => setFile(e.target.files?.[0] || null)}
//           />
//           <p className="text-gray-500">
//             {file ? file.name : "Click to select video"}
//           </p>
//         </label>

//         <button
//           onClick={handleUpload}
//           disabled={loading}
//           className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg transition disabled:opacity-50"
//         >
//           {loading ? "Uploading..." : "Upload"}
//         </button>

//         {videoId && (
//           <div className="text-center space-y-2">
//             <p className="text-sm text-gray-500">Video ID</p>
//             <code className="block text-xs bg-gray-100 p-2 rounded">
//               {videoId}
//             </code>

//             <a
//               href={`/status/${videoId}`}
//               className="text-blue-600 underline text-sm"
//             >
//               Check Status →
//             </a>
//           </div>
//         )}
//       </div>
//     </main>
//   );
// }

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const router = useRouter();
  
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [videoId, setVideoId] = useState<string | null>(null);

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });

      router.refresh();
      alert("Logged out.");
    } catch (err) {
      console.error(err);
      alert("Logout failed.");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 401) {
          alert("Please log in before uploading a video.");
          return;
        }

        throw new Error(`Upload failed (${res.status})`);
      }

      const data = await res.json();
      setVideoId(data.video_id);
    } catch (err) {
      console.error(err);
      alert("Upload failed. Check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto mb-6 flex max-w-5xl justify-end gap-4">
        <Link
          href="/login"
          className="text-sm font-medium text-gray-600 hover:text-black"
        >
          Login
        </Link>

        <Link
          href="/register"
          className="text-sm font-medium text-gray-600 hover:text-black"
        >
          Register
        </Link>

        <Link
          href="/dashboard"
          className="text-sm font-medium text-gray-600 hover:text-black"
        >
          Dashboard
        </Link>

        <button
          type="button"
          onClick={handleLogout}
          className="text-sm font-medium text-gray-600 hover:text-black"
        >
          Logout
        </button>
      </div>

      <div className="mx-auto max-w-5xl grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <p className="text-sm text-gray-500">Media Pipeline</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">
            Upload a video
          </h1>
          <p className="mt-3 text-gray-600">
            Send a video into the processing pipeline and track conversion
            progress in a live status dashboard.
          </p>

          <div className="mt-8 space-y-4">
            <label className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-6 text-center transition hover:border-blue-400 hover:bg-blue-50">
              <input
                type="file"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <p className="text-sm font-medium text-gray-700">
                {file ? file.name : "Click to select a video file"}
              </p>
              <p className="mt-2 text-xs text-gray-500">
                MP4 and similar formats supported
              </p>
            </label>

            <button
              onClick={handleUpload}
              disabled={loading}
              className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Uploading..." : "Start Processing"}
            </button>
          </div>

          {videoId && (
            <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <p className="text-sm font-semibold text-emerald-700">
                Upload successful
              </p>
              <p className="mt-2 break-all font-mono text-xs text-emerald-700">
                {videoId}
              </p>
              <a
                href={`/status/${videoId}`}
                className="mt-4 inline-flex text-sm font-medium text-emerald-700 underline"
              >
                Open status dashboard →
              </a>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">
            What happens next
          </h2>

          <div className="mt-6 space-y-4">
            <InfoStep
              number="01"
              title="Upload"
              description="Your video is stored in object storage and registered in Postgres."
            />
            <InfoStep
              number="02"
              title="Convert"
              description="A worker consumes the queue message and extracts MP3 audio with FFmpeg."
            />
            <InfoStep
              number="03"
              title="Deliver"
              description="The result is stored in the output bucket and exposed through the dashboard."
            />
          </div>
        </section>
      </div>
    </main>
  );
}

function InfoStep({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
        {number}
      </div>
      <div>
        <p className="font-semibold text-gray-900">{title}</p>
        <p className="mt-1 text-sm text-gray-600">{description}</p>
      </div>
    </div>
  );
}
