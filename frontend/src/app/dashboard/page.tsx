// import { cookies } from "next/headers";
// import { redirect } from "next/navigation";

// export default async function DashboardPage() {
//   const cookieStore = await cookies();
//   const accessToken = cookieStore.get("access_token");

//   const response = await fetch("http://upload-service:8000/auth/me", {
//     headers: {
//       Cookie: `access_token=${accessToken?.value}`,
//     },
//     cache: "no-store",
//   });

//   if (!response.ok) {
//     redirect("/login");
//   }

//   const user = await response.json();

//   return (
//     <main className="max-w-3xl mx-auto mt-10">
//       <h1 className="text-3xl font-bold">Welcome {user.email}</h1>
//       <p className="mt-4">You can now upload videos securely.</p>
//     </main>
//   );
// }

import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL || "http://upload-service:8000";

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  const res = await fetch(`${INTERNAL_API_URL}/auth/me`, {
    headers: {
      Cookie: `access_token=${accessToken}`,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    redirect("/login");
  }

  const user: { id: string; email: string } = await res.json();

  return (
    <main className="min-h-screen bg-gray-100 px-4 py-10">
      <div className="mx-auto max-w-3xl rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-gray-500">Account</p>
        <h1 className="mt-2 text-3xl font-bold text-gray-900">Dashboard</h1>

        <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-4">
          <p className="text-sm text-gray-500">Signed in as</p>
          <p className="mt-2 text-lg font-semibold text-gray-900">
            {user.email}
          </p>
        </div>

        <div className="mt-6 flex gap-4">
          <Link
            href="/"
            className="inline-flex rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Go to Upload
          </Link>
        </div>
      </div>
    </main>
  );
}
