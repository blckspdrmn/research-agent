// https://authjs.dev/getting-started/providers/microsoft-entra-id
import NextAuth from "next-auth";
import MicrosoftEntraID from "next-auth/providers/microsoft-entra-id";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    MicrosoftEntraID({
      clientId: process.env.AUTH_MICROSOFT_ENTRA_ID_ID,
      clientSecret: process.env.AUTH_MICROSOFT_ENTRA_ID_SECRET,
      issuer: process.env.AUTH_MICROSOFT_ENTRA_ID_ISSUER,
      // https://authjs.dev/guides/configuring-oauth-providers
      authorization: {
        params: {
          scope: `openid profile email ${process.env.AUTH_ENTRA_API_SCOPE}`,
        }, // https://learn.microsoft.com/ja-jp/entra/identity-platform/scopes-oidc#openid-connect-scopes
      },
    }),
  ],
  callbacks: {
    // https://authjs.dev/guides/integrating-third-party-backends#storing-the-token-in-the-session
    // https://authjs.dev/reference/nextjs#jwt
    jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token;
        token.expiresAt = account.expires_at;
      }
      return token;
    },
    // https://authjs.dev/reference/nextjs#session
    session({ session, token }) {
      session.accessToken = token.accessToken;
      session.expiresAt = token.expiresAt;
      return session;
    },
  },
});
