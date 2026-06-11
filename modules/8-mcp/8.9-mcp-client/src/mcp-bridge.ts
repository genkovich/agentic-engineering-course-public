// mcp-bridge.ts: міст між MCP-сервером і Claude API.
//
// Тут живе вся "магія" власного MCP-клієнта, і її напрочуд мало:
//
//   1. mcpToolsToAnthropic()  переклад опису tools з формату MCP
//      у формат, який приймає Claude Messages API.
//   2. executeToolUse()       виконання одного tool_use блоку від Claude
//      через MCP callTool і пакування відповіді у tool_result.
//   3. runToolLoop()          повний цикл: Claude думає, просить tool,
//      ми виконуємо через MCP, віддаємо результат, Claude продовжує.
//
// Обидва SDK говорять JSON Schema, тому конверсія зводиться до
// перейменування полів, дані не трансформуються.

import type Anthropic from "@anthropic-ai/sdk";
import type { Client } from "@modelcontextprotocol/sdk/client/index.js";

// Tool у форматі MCP (те, що повертає client.listTools()).
// Беремо структурний тип замість імпорту повної Zod-схеми з SDK,
// бо нам потрібні лише три поля.
export interface McpToolDefinition {
  name: string;
  description?: string;
  inputSchema: {
    type: "object";
    properties?: Record<string, unknown>;
    required?: string[];
    [key: string]: unknown;
  };
}

// Мінімальний інтерфейс Anthropic-клієнта, який потрібен циклу.
// Завдяки цьому в тестах можна підставити мок без реального API-ключа.
export interface MessagesApi {
  messages: {
    create(
      params: Anthropic.MessageCreateParamsNonStreaming,
    ): Promise<Anthropic.Message>;
  };
}

/**
 * Конвертує опис tools з MCP у формат tools Claude API.
 *
 * MCP:    { name, description, inputSchema }   (camelCase)
 * Claude: { name, description, input_schema }  (snake_case)
 *
 * Обидва формати містять JSON Schema об'єкта з properties/required,
 * тому схему передаємо як є, міняється тільки назва поля.
 */
export function mcpToolsToAnthropic(
  tools: McpToolDefinition[],
): Anthropic.Tool[] {
  return tools.map((tool) => ({
    name: tool.name,
    description: tool.description ?? "",
    input_schema: tool.inputSchema as Anthropic.Tool.InputSchema,
  }));
}

/**
 * Виконує один tool_use блок від Claude через MCP-сервер.
 *
 * 1. Claude каже: "виклич tool X з аргументами Y" (tool_use блок).
 * 2. Ми транслюємо це у MCP-виклик: client.callTool({name, arguments}).
 * 3. Відповідь сервера пакуємо у tool_result блок з тим самим id,
 *    щоб Claude знав, до якого виклику належить результат.
 *
 * Якщо сервер повернув isError або виклик впав, ставимо is_error: true.
 * Claude побачить помилку і зможе спробувати інший підхід.
 */
export async function executeToolUse(
  mcp: Client,
  toolUse: Anthropic.ToolUseBlock,
): Promise<Anthropic.ToolResultBlockParam> {
  try {
    const result = await mcp.callTool({
      name: toolUse.name,
      arguments: (toolUse.input ?? {}) as Record<string, unknown>,
    });

    return {
      type: "tool_result",
      tool_use_id: toolUse.id,
      content: mcpContentToText(result.content),
      is_error: result.isError === true ? true : undefined,
    };
  } catch (error) {
    // Транспортна або протокольна помилка. Її теж віддаємо Claude
    // як текст, а не валимо весь процес.
    return {
      type: "tool_result",
      tool_use_id: toolUse.id,
      content: `MCP call failed: ${error instanceof Error ? error.message : String(error)}`,
      is_error: true,
    };
  }
}

/**
 * MCP повертає масив content-блоків (text, image, resource...).
 * Для tool_result нам потрібен текст: текстові блоки склеюємо,
 * все інше серіалізуємо в JSON, щоб нічого не загубити.
 */
function mcpContentToText(content: unknown): string {
  if (!Array.isArray(content)) {
    return content === undefined ? "" : JSON.stringify(content);
  }
  return content
    .map((block) =>
      block?.type === "text" && typeof block.text === "string"
        ? block.text
        : JSON.stringify(block),
    )
    .join("\n");
}

export interface ToolLoopOptions {
  /** Anthropic-клієнт (або мок у тестах). */
  anthropic: MessagesApi;
  /** Підключений MCP-клієнт. */
  mcp: Client;
  /** Модель Claude. */
  model: string;
  /** Запит користувача. */
  userMessage: string;
  /** Системний промпт (опційно). */
  system?: string;
  /** Ліміт токенів відповіді. */
  maxTokens?: number;
  /** Запобіжник від нескінченного циклу. */
  maxIterations?: number;
  /** Колбеки для логування того, що відбувається. */
  onText?: (text: string) => void;
  onToolUse?: (name: string, input: unknown) => void;
  onToolResult?: (result: Anthropic.ToolResultBlockParam) => void;
}

/**
 * Повний tool-use loop: серце власного MCP-клієнта.
 *
 * Алгоритм (один-в-один як у Claude Code чи будь-якого агента):
 *
 *   1. Беремо tools у MCP-сервера і перекладаємо у формат Claude API.
 *   2. Шлемо запит користувача у Messages API разом зі списком tools.
 *   3. Якщо stop_reason === "tool_use", Claude хоче викликати інструмент:
 *      - додаємо відповідь Claude (з tool_use блоками) в історію;
 *      - виконуємо КОЖЕН tool_use через MCP callTool;
 *      - додаємо tool_result блоки як нове user-повідомлення;
 *      - повторюємо запит.
 *   4. Якщо stop_reason === "end_turn", Claude закінчив. Повертаємо текст.
 *
 * Повертає фінальний текст відповіді Claude.
 */
export async function runToolLoop(options: ToolLoopOptions): Promise<string> {
  const {
    anthropic,
    mcp,
    model,
    userMessage,
    system,
    maxTokens = 16000,
    maxIterations = 10,
    onText,
    onToolUse,
    onToolResult,
  } = options;

  // Крок 1: дізнаємось, що вміє сервер, і перекладаємо для Claude.
  const { tools: mcpTools } = await mcp.listTools();
  const tools = mcpToolsToAnthropic(mcpTools as McpToolDefinition[]);

  // Історія розмови. API стейтлес, тому щоразу шлемо її повністю.
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];

  let finalText = "";

  for (let iteration = 0; iteration < maxIterations; iteration++) {
    // Крок 2: запит у Claude зі списком доступних tools.
    // messages копіюємо, щоб кожен запит ніс свій знімок історії.
    const response = await anthropic.messages.create({
      model,
      max_tokens: maxTokens,
      ...(system ? { system } : {}),
      tools,
      messages: [...messages],
    });

    // Показуємо текстові блоки одразу. Claude часто коментує,
    // що збирається зробити, перед викликом інструмента.
    for (const block of response.content) {
      if (block.type === "text") {
        finalText = block.text;
        onText?.(block.text);
      }
    }

    // Крок 4: Claude закінчив, більше інструментів не потрібно.
    if (response.stop_reason !== "tool_use") {
      return finalText;
    }

    // Крок 3: Claude просить виконати інструменти.
    // Відповідь асистента (включно з tool_use блоками) ОБОВ'ЯЗКОВО
    // додаємо в історію, інакше API поверне 400.
    messages.push({ role: "assistant", content: response.content });

    const toolResults: Anthropic.ToolResultBlockParam[] = [];
    for (const block of response.content) {
      if (block.type === "tool_use") {
        onToolUse?.(block.name, block.input);
        const result = await executeToolUse(mcp, block);
        onToolResult?.(result);
        toolResults.push(result);
      }
    }

    // tool_result блоки йдуть як user-повідомлення і мусять стояти
    // одразу після assistant-повідомлення з tool_use.
    messages.push({ role: "user", content: toolResults });
  }

  throw new Error(
    `Tool loop did not finish in ${maxIterations} iterations: ` +
      "Claude keeps requesting tools.",
  );
}
