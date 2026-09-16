import type { NextConfig } from "next";

const securityHeaders = [
  // HTTPSを強制する(ブラウザが以後HTTPでのアクセスを自動でHTTPSに変える): https://qiita.com/rocinante-ein/items/8250ec6a6712a9dcb96a
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains",
  },
  // Content-Typeの推測(MIMEスニッフィング)を禁止する: https://qiita.com/ktdatascience/items/80966bfc1bb2ee2c42ea
  { key: "X-Content-Type-Options", value: "nosniff" },
  // 他サイトのiframeに埋め込ませない(クリックジャッキング対策): https://qiita.com/gotchane/items/4d31b01381f47100de7f
  { key: "X-Frame-Options", value: "DENY" },
  // 別サイトへ遷移するとき、URLのパスやクエリを送らない: https://qiita.com/c0ridrew/items/7f2c9dad12543fa2662f
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
];

const nextConfig: NextConfig = {
  output: "standalone", // https://nextjs.org/docs/pages/api-reference/config/next-config-js/output#automatically-copying-traced-files
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};

export default nextConfig;
