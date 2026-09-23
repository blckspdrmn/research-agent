// https://authjs.dev/getting-started/session-management/login#signout
import { signOut } from "@/auth";
export async function POST() {
  await signOut({ redirect: false });
  const url = new URL(process.env.AUTH_ENTRA_LOGOUT_URL!);
  url.searchParams.set(
    "post_logout_redirect_uri",
    `${process.env.AUTH_URL}/login`,
  );
  return Response.redirect(url, 303);
}
