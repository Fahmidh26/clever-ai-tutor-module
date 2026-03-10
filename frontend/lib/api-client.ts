export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  headers?: Record<string, string>;
  retries?: number;
  credentials?: RequestCredentials;
  signal?: AbortSignal;
};

type ApiClientOptions = {
  baseUrl: string;
  onUnauthorized?: () => void;
};

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function shouldRetry(status: number): boolean {
  return status === 408 || status === 429 || status >= 500;
}

async function parseResponse(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

export function createApiClient(options: ApiClientOptions) {
  const request = async <T>(path: string, config: RequestOptions = {}): Promise<T> => {
    const {
      method = "GET",
      body,
      headers = {},
      retries = 2,
      credentials = "include",
      signal,
    } = config;

    let attempt = 0;
    while (attempt <= retries) {
      const response = await fetch(`${options.baseUrl}${path}`, {
        method,
        credentials,
        signal,
        headers: {
          Accept: "application/json",
          ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
          ...headers,
        },
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });

      if (response.status === 401 && options.onUnauthorized) {
        options.onUnauthorized();
      }

      const payload = await parseResponse(response);
      if (response.ok) {
        return payload as T;
      }

      const canRetry = shouldRetry(response.status) && attempt < retries;
      if (canRetry) {
        const backoffMs = 200 * 2 ** attempt;
        await sleep(backoffMs);
        attempt += 1;
        continue;
      }

      const message =
        typeof payload === "string"
          ? payload
          : ((payload as { message?: string; error?: string })?.message ??
            (payload as { message?: string; error?: string })?.error ??
            `Request failed (${response.status})`);

      throw new ApiError(message, response.status, payload);
    }

    throw new ApiError("Request failed after retry attempts", 0, null);
  };

  return {
    get: <T>(path: string, config?: Omit<RequestOptions, "method" | "body">) =>
      request<T>(path, { ...config, method: "GET" }),
    post: <T>(path: string, body?: unknown, config?: Omit<RequestOptions, "method" | "body">) =>
      request<T>(path, { ...config, method: "POST", body }),
    put: <T>(path: string, body?: unknown, config?: Omit<RequestOptions, "method" | "body">) =>
      request<T>(path, { ...config, method: "PUT", body }),
    patch: <T>(path: string, body?: unknown, config?: Omit<RequestOptions, "method" | "body">) =>
      request<T>(path, { ...config, method: "PATCH", body }),
    del: <T>(path: string, config?: Omit<RequestOptions, "method" | "body">) =>
      request<T>(path, { ...config, method: "DELETE" }),
  };
}
