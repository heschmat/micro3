// "use client";

// import { useRouter } from "next/navigation";
// import { useState } from "react";
// import { apiFetch } from "@/lib/api";

// export default function RegisterPage() {
//   const router = useRouter();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   async function handleRegister(e: React.FormEvent) {
//     e.preventDefault();

//     const response = await apiFetch("/auth/register", {
//       method: "POST",
//       body: JSON.stringify({ email, password }),
//     });

//     if (!response.ok) {
//       alert("Registration failed");
//       return;
//     }

//     router.push("/login");
//   }

//   return (
//     <main className="max-w-md mx-auto mt-20">
//       <h1 className="text-2xl font-bold mb-6">Register</h1>

//       <form onSubmit={handleRegister} className="space-y-4">
//         <input
//           className="border p-2 w-full"
//           placeholder="Email"
//           value={email}
//           onChange={(e) => setEmail(e.target.value)}
//         />

//         <input
//           className="border p-2 w-full"
//           type="password"
//           placeholder="Password"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//         />

//         <button className="bg-black text-white px-4 py-2 rounded">
//           Register
//         </button>
//       </form>
//     </main>
//   );
// }

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RegisterPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);

      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!res.ok) {
        if (res.status === 409) {
          alert("That email is already registered.");
          return;
        }

        throw new Error(`Registration failed (${res.status})`);
      }

      alert("Registration successful. Please log in.");
      router.push("/login");
    } catch (err) {
      console.error(err);
      alert("Registration failed. Check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-8">
          <p className="text-sm text-gray-500">Authentication</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Register</h1>
          <p className="mt-3 text-gray-600">
            Create an account to upload videos and securely access your audio files.
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 outline-none transition focus:border-blue-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Choose a password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-sm text-gray-600">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-blue-600 underline">
            Login
          </Link>
        </p>
      </div>
    </main>
  );
}
