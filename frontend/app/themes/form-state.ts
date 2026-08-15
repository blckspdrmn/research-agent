// フォームの実行結果（Server Actionsの返却値）の型
export type FormState = {
  status: "idle" | "success" | "error";
  message: string | null;
};

export const initialFormState: FormState = { status: "idle", message: null };
