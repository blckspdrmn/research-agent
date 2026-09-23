// https://authjs.dev/getting-started/typescript#module-augmentation
import "next-auth/jwt";

declare module "next-auth/jwt" {
  interface JWT {
    apiAccessToken?: string;
    apiExpiresAt?: number;
  }
}
