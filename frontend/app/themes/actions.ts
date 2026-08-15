"use server";

import { revalidatePath } from "next/cache";
import {
  ApiError,
  createThemeRequest,
  deleteThemeRequest,
  updateThemeRequest,
} from "@/lib/api";

import type { FormState } from "./form-state";

function parseThemeForm(formData: FormData): {
  title: string;
  description: string | null;
  error?: FormState;
} {
  const title = String(formData.get("title") ?? "").trim();
  const description = String(formData.get("description") ?? "").trim();

  if (title.length === 0) {
    return {
      title,
      description: null,
      error: { status: "error", message: "テーマ名を入力してください" },
    };
  }
  if (title.length > 100) {
    return {
      title,
      description: null,
      error: {
        status: "error",
        message: "テーマ名は100文字以内で入力してください",
      },
    };
  }

  return { title, description: description || null };
}

export async function createTheme(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  const { title, description, error } = parseThemeForm(formData);
  if (error) return error;

  try {
    await createThemeRequest({ title, description });
  } catch (e) {
    if (e instanceof ApiError && e.status === 422) {
      // 422はPydanticバリデーションエラーのステータスコード
      return { status: "error", message: "入力内容が不正です" };
    }
    throw e; // 想定外はerror.tsxに任せる
  }

  revalidatePath("/themes");
  return { status: "success", message: null };
}

export async function updateTheme(
  id: string,
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  const { title, description, error } = parseThemeForm(formData);
  if (error) return error;

  try {
    await updateThemeRequest(id, { title, description: description || null });
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return { status: "error", message: "このテーマは既に削除されています" };
    }
    if (e instanceof ApiError && e.status === 422) {
      return { status: "error", message: "入力内容が不正です" };
    }
    throw e;
  }

  revalidatePath("/themes");
  return { status: "success", message: null };
}

export async function deleteTheme(
  id: string,
  _prevState: FormState,
): Promise<FormState> {
  try {
    await deleteThemeRequest(id);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return { status: "error", message: "このテーマは既に削除されています" };
    }
    throw e;
  }
  revalidatePath("/themes");
  return { status: "success", message: null };
}
