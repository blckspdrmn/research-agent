"use server";

import { revalidatePath } from "next/cache";
import { ApiError } from "@/lib/api/client";
import {
  createThemeRequest,
  deleteThemeRequest,
  updateThemeRequest,
} from "@/lib/api/themes";
import { runResearchRequest } from "@/lib/api/reports";

import type { FormState } from "./form-state";

function parseThemeForm(formData: FormData): {
  title: string;
  preferred_domains: string[] | null;
  report_depth: string;
  description: string | null;
  error?: FormState;
} {
  const title = String(formData.get("title") ?? "").trim();
  const domainsRaw = String(formData.get("preferred_domains") ?? "").trim();
  const report_depth = String(formData.get("report_depth") ?? "standard");
  const description = String(formData.get("description") ?? "").trim();

  if (title.length === 0) {
    return {
      title,
      preferred_domains: null,
      report_depth,
      description: null,
      error: { status: "error", message: "テーマ名を入力してください" },
    };
  }
  if (title.length > 100) {
    return {
      title,
      preferred_domains: null,
      report_depth,
      description: null,
      error: {
        status: "error",
        message: "テーマ名は100文字以内で入力してください",
      },
    };
  }

  // カンマ区切りでドメインを分割、空文字を除去
  const preferred_domains = domainsRaw
    ? domainsRaw
        .split(",")
        .map((d) => d.trim())
        .filter(Boolean)
    : null;

  return {
    title,
    preferred_domains,
    report_depth,
    description: description || null,
  };
}

export async function createTheme(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  const { title, preferred_domains, report_depth, description, error } =
    parseThemeForm(formData);
  if (error) return error;

  try {
    await createThemeRequest({
      title,
      preferred_domains,
      report_depth,
      description,
    });
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
  const { title, preferred_domains, report_depth, description, error } =
    parseThemeForm(formData);
  if (error) return error;

  try {
    await updateThemeRequest(id, {
      title,
      preferred_domains,
      report_depth,
      description,
    });
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

export async function runResearch(
  id: string,
  _prevState: FormState,
): Promise<FormState> {
  try {
    await runResearchRequest(id);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return { status: "error", message: "このテーマは既に削除されています" };
    }
    throw e;
  }
  revalidatePath(`/themes/${id}`);
  return { status: "success", message: null };
}
