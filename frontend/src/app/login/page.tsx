// "use client";

// import { useRouter } from "next/navigation";
// import { useState } from "react";
// import { apiFetch } from "@/lib/api";

// export default function LoginPage() {
//   const router = useRouter();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   async function handleLogin(e: React.FormEvent) {
//     e.preventDefault();

//     const response = await apiFetch("/auth/login", {
//       method: "POST",
//       body: JSON.stringify({ email, password }),
//     });

//     if (!response.ok) {
//       alert("Invalid login");
//       return;
//     }

//     router.push("/dashboard");
//     router.refresh();
//   }

//   return (
//     <main className="max-w-md mx-auto mt-20">
//       <h1 className="text-2xl font-bold mb-6">Login</h1>

//       <form onSubmit={handleLogin} className="space-y-4">
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
//           Login
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

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);

      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!res.ok) {
        if (res.status === 401) {
          alert("Invalid email or password.");
          return;
        }

        throw new Error(`Login failed (${res.status})`);
      }

      router.push("/");
      router.refresh();
    } catch (err) {
      console.error(err);
      alert("Login failed. Check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-8">
          <p className="text-sm text-gray-500">Authentication</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Login</h1>
          <p className="mt-3 text-gray-600">
            Sign in to upload videos and access your conversion jobs.
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
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
              placeholder="Your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        <p className="mt-6 text-sm text-gray-600">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-blue-600 underline">
            Register
          </Link>
        </p>
      </div>
    </main>
  );
}
